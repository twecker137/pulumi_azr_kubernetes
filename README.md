# Azure AKS Pulumi Deployment

## Needed permissions

| Scope    | Permission                       | Description |
|----------|--------------| ----------- |
| Subscription | `User Access Administrator` | Required to manage permissions for the application |

## Needed features for GitOps

| Scope    | Feature                     | Description |
|----------|-----------------------------|-------------|
| Subscription | `az feature register --namespace Microsoft.ContainerService --name AKS-ExtensionManager` | https://docs.microsoft.com/en-us/azure/azure-arc/kubernetes/tutorial-use-gitops-flux2            |
| Subscription | `az provider register --namespace Microsoft.KubernetesConfiguration` | https://docs.microsoft.com/en-us/azure/azure-arc/kubernetes/tutorial-use-gitops-flux2            |
