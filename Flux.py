import pulumi
import pulumi_kubernetes as k8s
from pulumi_kubernetes.helm.v3 import Chart, ChartOpts

from pulumi import ResourceOptions


class FluxDeploymentArgs:
    def __init__(self, kubeconfig):
        self.kubeconfig = kubeconfig


class FluxDeployment(pulumi.ComponentResource):
    def __init__(self,
                 name: str,
                 args: FluxDeploymentArgs,
                 opts: ResourceOptions = None):
        super().__init__("towe:modules:Flux", name, {}, opts)

        self.k8s_provider = k8s.Provider('k8s-provider', kubeconfig=args.kubeconfig)

