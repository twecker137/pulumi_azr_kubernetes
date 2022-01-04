import sys
import os
import json
import base64
import pulumi
from pulumi import automation as auto, ResourceOptions
import pulumi_azure_native as azure_native

from dotenv import load_dotenv
from pathlib import Path

import Networking
import AKS

dotenv_path = Path('dev.env')
load_dotenv(dotenv_path=dotenv_path)

admin_user = os.getenv('ADMIN_USER')
admin_ssh_pubkey = os.getenv('ADMIN_SSH_PUBKEY')
access_source_address_prefix = os.getenv('ACCESS_SOURCE_ADDRESS_PREFIX')


def pulumi_program():
    rg_network = azure_native.resources.ResourceGroup(resource_name="aks-%s-net" % stack_name)
    networks = Networking.SpokeNetwork("spoke", Networking.SpokeNetworkArgs(
        name="spoke",
        location=rg_network.location,
        networks={
            'vnets': [
                {
                    'name': 'vnet-01',
                    'resource_group_name': rg_network.name,
                    'address_prefixes': ['10.1.0.0/16', '10.2.0.0/16'],
                    'subnets': [
                        {
                            'name': 'snet-01',
                            'address_prefix': '10.1.0.0/24'
                        },
                        {
                            'name': 'snet-02',
                            'address_prefix': '10.2.0.0/24'
                        }
                    ]
                }
            ]
        }
    ))

    rg_aks = azure_native.resources.ResourceGroup(resource_name="aks-%s-aks" % stack_name)
    cluster = AKS.AKSCluster("cluster-01", AKS.AKSClusterArgs(
        location=rg_aks.location,
        resource_group_name=rg_aks.name,
        admin_user=admin_user,
        admin_ssh_pubkey=admin_ssh_pubkey,
        kubernetes_version="1.22.4",
        agent_pool_profiles=[azure_native.containerservice.ManagedClusterAgentPoolProfileArgs(
            name="nodepool01",
            count=3,
            enable_node_public_ip=False,
            mode="System",
            os_type="Linux",
            vm_size="Standard_D2_v2",
            type="VirtualMachineScaleSets",
            availability_zones=["1", "2", "3"],
            vnet_subnet_id=networks.virtual_networks[0].subnets[1].id.apply(lambda sid: sid)
        )],
        auto_scaler_profile=azure_native.containerservice.ManagedClusterPropertiesAutoScalerProfileArgs(
            scale_down_delay_after_add="15m",
            scan_interval="20s",
        ),
    ))

    encoded = cluster.cluster_credentials.kubeconfigs[0].value
    kubeconfig = encoded.apply(
        lambda enc: base64.b64decode(enc).decode()
    )
    pulumi.export("kubeconfig", kubeconfig)

# To destroy our program, we can run python main.py destroy
destroy = False
# To preview our program, we can run python main.py preview
preview = False
args = sys.argv[1:]
if len(args) > 0:
    if args[0] == "destroy":
        destroy = True
    elif args[0] == "preview":
        preview = True

project_name = "azure-kubernetes"
# We use a simple stack name here, but recommend using auto.fully_qualified_stack_name for maximum specificity.
stack_name = "dev"
# stack_name = auto.fully_qualified_stack_name("myOrgOrUser", project_name, stack_name)

# create or select a stack matching the specified name and project.
# this will set up a workspace with everything necessary to run our inline program (pulumi_program)
stack = auto.create_or_select_stack(stack_name=stack_name,
                                    project_name=project_name,
                                    program=pulumi_program)

print("successfully initialized stack")

# for inline programs, we must manage plugins ourselves
print("installing plugins...")
stack.workspace.install_plugin("azure-native", "v1.52.0")
print("plugins installed")

# set stack configuration specifying the Azure region to deploy
print("setting up config")
stack.set_config("azure-native:location", auto.ConfigValue(value=os.getenv('AZURE_LOCATION')))

print("config set")

print("refreshing stack...")
stack.refresh(on_output=print)
print("refresh complete")

if destroy:
    print("destroying stack...")
    stack.destroy(on_output=print)
    print("stack destroy complete")
    sys.exit()

if preview:
    print("stack preview")
    up_res = stack.preview(on_output=print)
    print(f"preview summary: \n{json.dumps(up_res.change_summary, indent=4)}")
    sys.exit()

print("updating stack...")
up_res = stack.up(on_output=print)
print(f"update summary: \n{json.dumps(up_res.summary.resource_changes, indent=4)}")
