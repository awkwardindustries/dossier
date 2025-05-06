# Samples for Azure Container Apps | Serverless GPU

Source: https://learn.microsoft.com/en-us/azure/container-apps/gpu-image-generation?pivots=azure-cli

This covers setting up ACA to use a serverless GPU workload profile and create an app that utilizes GPU.

*Looking for [NVIDIA NIMs](NVIDIA-NIMs.md) instead?*

## Notes
- Customers with EAs and pay-as-you-go customers have A100 and T4 quota enabled by default
- Only available in preview in:
   - West US 3
   - Australia East
   - Sweden Central

## Run the quickstart sample

```bash
# Assign variables

RESOURCE_GROUP=eph-rg-aca-serverless-gpu
LOCATION=westus3
ACR_NAME=acrgputests
ENVIRONMENT_NAME=serverless-gpu-tests
CONTAINER_APP_NAME=gpu-app
WORKLOAD_PROFILE_NAME="NC8as-T4"
WORKLOAD_PROFILE_TYPE="Consumption-GPU-NC8as-T4"
SOURCE_CONTAINER_IMAGE_REPO="mcr.microsoft.com/"
CONTAINER_IMAGE_NAME="k8se/gpu-quickstart:latest"
IDENTITY="id-serverless-gpu-tests"

# Create the resource group

az group create -n $RESOURCE_GROUP -l $LOCATION

# NOTES:
# In "container" tab... under "container resource allocation", check GPU checkbox.
# For the "GPU Type" select either 'NVIDIA A100' or 'NVIDIA T4'
# create a consumption GPU workload profile
# enable artifact streaming on ACR

# Create a container registry

az acr create \
--resource-group $RESOURCE_GROUP \
--location $LOCATION \
--name $ACR_NAME \
--sku premium

az acr import \
--name $ACR_NAME \
--source ${SOURCE_CONTAINER_IMAGE_REPO}${CONTAINER_IMAGE_NAME}

# Enable artifact streaming (at repository and image)

az acr artifact-streaming update \
--name $ACR_NAME \
--repository "${CONTAINER_IMAGE_NAME%%:*}" \
--enable-streaming True

az acr artifact-streaming create \
--name $ACR_NAME \
--image $CONTAINER_IMAGE_NAME

# Create container app environment

az containerapp env create \
--name $ENVIRONMENT_NAME \
--resource-group $RESOURCE_GROUP \
--location $LOCATION

# Add a workload profile to the environment

az containerapp env workload-profile add \
--name $ENVIRONMENT_NAME \
--resource-group $RESOURCE_GROUP \
--workload-profile-name $WORKLOAD_PROFILE_NAME \
--workload-profile-type $WORKLOAD_PROFILE_TYPE

# Create user-assigned managed identity

az identity create \
--name $IDENTITY \
--resource-group $RESOURCE_GROUP

IDENTITY_ID=$(az identity show --name $IDENTITY --resource-group $RESOURCE_GROUP --query id --output tsv)

# Create the container app

# Note: The command will automatically add the 'acrpull' to the 
# specified user-assigned managed identity targeting the defined registry.
# Typically this assignment would need to be explicitly made as a
# separate operation.

az containerapp create \
--name $CONTAINER_APP_NAME \
--resource-group $RESOURCE_GROUP \
--environment $ENVIRONMENT_NAME \
--user-assigned $IDENTITY_ID \
--registry-identity $IDENTITY_ID \
--registry-server "${ACR_NAME}.azurecr.io" \
--image "${ACR_NAME}.azurecr.io/${CONTAINER_IMAGE_NAME}" \
--target-port 80 \
--ingress external \
--cpu 8.0 \
--memory 56.0Gi \
--workload-profile-name $WORKLOAD_PROFILE_NAME
```

## Test

> Note: It may take up to **five minutes** for the container app to start up.

1. Open the application and generate an image.
2. Navigate to the Azure Container App view in the Azure Portal for the *gpu-app*.
   0. Confirm the GPU status:
      1. Expand the Monitoring section.
      2. Click on Console.
      3. From the (default view) App container console, ensure the Replica and *gpu-app* Container are selected.
      4. From the Choose start up command overlay window
         1. Choose the */bin/bash* start up command
         2. Select Connect
      5. Once the shell is set up, enter the command `nvidia-smi` to review the status and output of your GPU.
   1. Watch application logs during image generation:
      1. From the monitoring section, click on Log stream.
      2. Select Real-time, Application, and revision/replica/container.
      3. Watch the live output logs from the container as you generate an image.
