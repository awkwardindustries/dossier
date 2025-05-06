# NVIDIA NIMs on ACA Serverless GPU

```bash
# Ensure you have the containerapp extension latest with preview features enabled

az extension add --name containerapp --upgrade --allow-preview true

# Register required provider namespaces

az provider register --namespace Microsoft.App
az provider register --namespace Microsoft.OperationalInsights

# Setup environment variables

RESOURCE_GROUP=eph-rg-nvidia-nims
LOCATION=westus3
SUB_ID=$(az account show -o tsv --query id)
SUFFIX=$(cksum <<< "${RESOURCE_GROUP}${SUB_ID}" | cut -f 1 -d ' ')

ACR_NAME="acrnvidianims${SUFFIX}"
ENVIRONMENT_NAME=nvidianims-tests
WORKLOAD_PROFILE_NAME="LLAMA_PROFILE"
WORKLOAD_PROFILE_TYPE="Consumption-GPU-NC24-A100"
CONTAINER_APP_NAME="llama3-nim"
CONTAINER_AND_TAG="llama-3.2-3b-instruct:latest"
IDENTITY="id-nvidianims-tests"

STORAGE_ACCOUNT_NAME="stnims${SUFFIX}"
STORAGE_SHARE_NAME="nimsfileshare"
STORAGE_MOUNT_NAME="nimsstoragemount"

# Note: If you don't already have one, you can get an API key from 
# the NVIDIA GPU Cloud (NGC) website: https://catalog.ngc.nvidia.com/
NVIDIA_API_KEY=<your key here>

# Creaete the resource group

az group create \
--name $RESOURCE_GROUP \
--location $LOCATION

# Create the container registry and import NIM image

az acr create \
--resource-group $RESOURCE_GROUP \
--name $ACR_NAME \
--location $LOCATION \
--sku premium

az acr import \
--name $ACR_NAME \
--source "nvcr.io/nim/meta/${CONTAINER_AND_TAG}" \
--image $CONTAINER_AND_TAG \
--username "\$oauthtoken" \
--password $NVIDIA_API_KEY

# Enable artifact streaming on registry and image

az acr artifact-streaming update \
--name $ACR_NAME \
--repository "${CONTAINER_AND_TAG%%:*}" \
--enable-streaming True

az acr artifact-streaming create \
--name $ACR_NAME \
--image $CONTAINER_AND_TAG

# Setup the storage account for volume mount

az storage account create \
--resource-group $RESOURCE_GROUP \
--name $STORAGE_ACCOUNT_NAME \
--location "$LOCATION" \
--kind StorageV2 \
--sku Standard_LRS \
--enable-large-file-share

az storage share-rm create \
--resource-group $RESOURCE_GROUP \
--storage-account $STORAGE_ACCOUNT_NAME \
--name $STORAGE_SHARE_NAME \
--quota 1024 \
--enabled-protocols SMB \
--output table

STORAGE_ACCOUNT_KEY=$(az storage account keys list -n $STORAGE_ACCOUNT_NAME --query "[0].value" -o tsv)

# Create the container app env and stuff...

az containerapp env create \
--name $ENVIRONMENT_NAME \
--resource-group $RESOURCE_GROUP \
--location $LOCATION \
--enable-workload-profiles

az containerapp env workload-profile add \
--resource-group $RESOURCE_GROUP \
--name $ENVIRONMENT_NAME \
--workload-profile-type $WORKLOAD_PROFILE_TYPE \
--workload-profile-name $WORKLOAD_PROFILE_NAME

az identity create \
--name $IDENTITY \
--resource-group $RESOURCE_GROUP

IDENTITY_ID=$(az identity show --name $IDENTITY --resource-group $RESOURCE_GROUP --query id --output tsv)

az containerapp env storage set \
--access-mode ReadWrite \
--azure-file-account-name $STORAGE_ACCOUNT_NAME \
--azure-file-account-key $STORAGE_ACCOUNT_KEY \
--azure-file-share-name $STORAGE_SHARE_NAME \
--storage-name $STORAGE_MOUNT_NAME \
--name $ENVIRONMENT_NAME \
--resource-group $RESOURCE_GROUP \
--output table

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
--image "${ACR_NAME}.azurecr.io/${CONTAINER_AND_TAG}" \
--target-port 8000 \
--ingress external \
--cpu 24 \
--memory 220.0Gi \
--secrets ngc-api-key=$NVIDIA_API_KEY \
--env-vars NGC_API_KEY=secretref:ngc-api-key \
--workload-profile-name $WORKLOAD_PROFILE_NAME

# DIRECT TEST
az containerapp create \
--name $CONTAINER_APP_NAME-direct \
--resource-group $RESOURCE_GROUP \
--environment $ENVIRONMENT_NAME \
--user-assigned $IDENTITY_ID \
--registry-server nvcr.io \
--registry-username "\$oauthtoken" \
--registry-password "secretref:ngc-api-key" \
--image "nvcr.io/nim/meta/${CONTAINER_AND_TAG}" \
--target-port 8000 \
--ingress external \
--cpu 24.0 \
--memory 220.0Gi \
--secrets ngc-api-key=$NVIDIA_API_KEY \
--env-vars NGC_API_KEY=secretref:ngc-api-key \
--workload-profile-name $WORKLOAD_PROFILE_NAME

# Setup the volume mount and update

az containerapp show \
--name $CONTAINER_APP_NAME-direct \
--resource-group $RESOURCE_GROUP \
--output yaml > app.yaml

# Make edits locally manually...then apply

az containerapp update \
--name $CONTAINER_APP_NAME \
--resource-group $RESOURCE_GROUP \
--yaml app.yaml \
--output table

```



Test it

```bash
CONTAINER_APP_FQDN=$(az containerapp show -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP --query properties.configuration.ingress.fqdn -o tsv)

curl -X POST "http://$APP_URL/v1/completions" \
-H "accept: application/json" \
-H "Content-Type: application/json" \
-d '{
  "model": "meta/llama-3.1-8b-instruct",
  "prompt":  [{"role":"user", "content":"Once upon a time..."}],
  "max_tokens": 64
}'
```