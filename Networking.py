import pulumi
import pulumi_azure_native as azure_native
from pulumi import ResourceOptions


class SpokeNetworkArgs:
    def __init__(self, name, location, networks):
        self.name = name
        self.location = location
        self.networks = networks

        @property
        def name(self):
            """Get the network name"""
            return self._name

        @name.setter
        def name(self, value):
            if len(value) > 20:
                raise ValueError("Name cannot exceed 20 characters.")
            self._name = value

        @property
        def network(self):
            """Get the network output"""
            return self._network


class SpokeNetwork(pulumi.ComponentResource):
    def __init__(self,
                 name: str,
                 args: SpokeNetworkArgs,
                 opts: ResourceOptions = None):
        super().__init__("towe:modules:SpokeNetwork", name, {}, opts)

        child_opts = ResourceOptions(parent=opts)

        self.virtual_networks = []
        for k, v in args.networks.items():
            for vnet in v:
                subnet_list = []
                for subnet in vnet['subnets']:
                    subnet_list.append(azure_native.network.SubnetArgs(
                        address_prefix=subnet['address_prefix'],
                        name=subnet['name']
                    ))

                self.virtual_networks.append(azure_native.network.VirtualNetwork(
                    "virtualNetwork",
                    address_space=azure_native.network.AddressSpaceArgs(
                        address_prefixes=vnet['address_prefixes']
                    ),
                    subnets=subnet_list,
                    location=args.location,
                    resource_group_name=vnet['resource_group_name'],
                    virtual_network_name=vnet['name'],
                    opts=ResourceOptions(parent=self))
                )

        self.register_outputs({})
