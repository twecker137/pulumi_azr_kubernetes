import pulumi
import pulumi_azure_native as azure_native
import pulumi_azuread as azuread

from pulumi import ResourceOptions


class AKSClusterArgs:
    def __init__(self, location, resource_group_name, agent_pool_profiles, auto_scaler_profile, admin_user,
                 admin_ssh_pubkey, kubernetes_version):
        self.location = location
        self.resource_group_name = resource_group_name
        self.agent_pool_profiles = agent_pool_profiles
        self.auto_scaler_profile = auto_scaler_profile
        self.admin_user = admin_user
        self.admin_ssh_pubkey = admin_ssh_pubkey
        self.kubernetes_version = kubernetes_version


class AKSCluster(pulumi.ComponentResource):
    def __init__(self,
                 name: str,
                 args: AKSClusterArgs,
                 opts: ResourceOptions = None):
        super().__init__("towe:modules:AKS", name, {}, opts)

        child_opts = ResourceOptions(parent=opts)

        self.ad_app = azuread.Application(name, display_name=name)
        self.ad_sp = azuread.ServicePrincipal(name, application_id=self.ad_app.application_id)
        self.ad_sp_password = azuread.ServicePrincipalPassword(name, service_principal_id=self.ad_sp.id)

        self.managed_cluster = azure_native.containerservice.ManagedCluster(
            name,
            location=args.location,
            resource_group_name=args.resource_group_name,
            agent_pool_profiles=args.agent_pool_profiles,
            auto_scaler_profile=args.auto_scaler_profile,
            disk_encryption_set_id=None,  # TODO: Add disk encryption set
            dns_prefix=name,  # TODO: Add DNS prefix
            enable_pod_security_policy=False,  # TODO: Add pod security policy or better OPA
            enable_rbac=True,
            kubernetes_version=args.kubernetes_version,
            linux_profile=azure_native.containerservice.ContainerServiceLinuxProfileArgs(
                admin_username=args.admin_user,
                ssh=azure_native.containerservice.ContainerServiceSshConfigurationArgs(
                    public_keys=[azure_native.containerservice.ContainerServiceSshPublicKeyArgs(
                        key_data=args.admin_ssh_pubkey
                    )]
                )
            ),
            network_profile=azure_native.containerservice.ContainerServiceNetworkProfileArgs(
                # TODO: Add network profile
                network_plugin="azure",
                network_policy="calico",
                load_balancer_profile=azure_native.containerservice.ManagedClusterLoadBalancerProfileArgs(
                    managed_outbound_ips=azure_native.containerservice.ManagedClusterLoadBalancerProfileManagedOutboundIPsArgs(
                        count=2,
                    ),
                ),
                load_balancer_sku="standard",
                outbound_type="loadBalancer",
            ),
            sku=azure_native.containerservice.ManagedClusterSKUArgs(
                name="Basic",
                tier="Free"
            ),
            service_principal_profile={
                "client_id": self.ad_app.application_id,
                "secret": self.ad_sp_password.value
            },
            # TODO: Add windows profile if needed
            opts=ResourceOptions(parent=self)
        )

        self.cluster_credentials = azure_native.containerservice.list_managed_cluster_user_credentials_output(
            resource_name=self.managed_cluster.name,
            resource_group_name=args.resource_group_name
        )

        self.register_outputs({})
