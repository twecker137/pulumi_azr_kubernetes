# Azure AKS Pulumi Deployment

## Description

This is a simple example of an Azure AKS cluster deployment using Pulumi and the Pulumi Automation API.

For executing the deployment, you will need to create a Service Principal or Managed Identity with the below-mentioned permissions.
There is a template for assigning the appropriate environment variables: [env.template](env.template)

```shell
# Execute pulumi preview
python __main__.py preview

# Execute pulumi up
python __main__.py

# Execute pulumi destroy
python __main__.py destroy
```

For more information about the Pulumi Automation API, see [Pulumi Automation API](https://www.pulumi.com/docs/reference/pulumi-automation-api/).

## Needed permissions

| Scope    | Permission                       | Description |
|----------|--------------| ----------- |
| Subscription | `User Access Administrator` | Required to manage permissions for the application |

## Needed features for GitOps

| Scope    | Feature                     | Description |
|----------|-----------------------------|-------------|
| Subscription | `az feature register --namespace Microsoft.ContainerService --name AKS-ExtensionManager` | https://docs.microsoft.com/en-us/azure/azure-arc/kubernetes/tutorial-use-gitops-flux2            |
| Subscription | `az provider register --namespace Microsoft.KubernetesConfiguration` | https://docs.microsoft.com/en-us/azure/azure-arc/kubernetes/tutorial-use-gitops-flux2            |
