# Samples for Azure Container Apps | Kaito

## Kubernetes AI Toolchain Operator (Kaito) on ACA

Project Kaito: https://github.com/kaito-project/kaito

Kaito helps automate AI/ML model inferencing workloads in a Kubernetes cluster. The project is supported by an operator to help with provisioning nodes based on model requirements. The project also hosts large model images in the public Microsoft Container Registry (MCR) if the license allows. This in theory supports deployment to ACA. This guide walks through how to deploy a Kaito-managed model image to an Azure Container Apps environment.

## Run the sample

### Deploy the inferencing model image

```bash
# Assign variables

RESOURCE_GROUP=rg-aca-kaito
LOCATION=westus3
CONTAINER_APP_ENV=kaito-tests
CONTAINER_APP=kaito-test-app
KAITO_MODEL_IMAGE=phi-3.5-mini-instruct
KAITO_MODEL_TAG=0.0.2

# Create the resource group

az group create -n $RESOURCE_GROUP -l $LOCATION

# Create the Azure Container Apps environments

az containerapp env create \
-n $CONTAINER_APP_ENV \
-g $RESOURCE_GROUP \
-l $LOCATION \
--enable-workload-profiles

# Create the GPU workload profile

az containerapp env workload-profile add \
--name $CONTAINER_APP_ENV \
--resource-group $RESOURCE_GROUP \
--workload-profile-name gpu-consumption \
--workload-profile-type Consumption-GPU-NC8as-T4 \
--max-nodes 1

# Deploy Kaito model image as application

az containerapp create -n $CONTAINER_APP -g $RESOURCE_GROUP \
--environment $CONTAINER_APP_ENV \
--image mcr.microsoft.com/aks/kaito/kaito-$KAITO_MODEL_IMAGE:$KAITO_MODEL_TAG \
--ingress external \
--target-port 80 \
--workload-profile-name gpu-consumption
```

### Test the inferencing endpoint

```bash
# Get the URL
ENDPOINT_FQDN=$(az containerapp show -n $CONTAINER_APP -g $RESOURCE_GROUP \
--query properties.configuration.ingress.fqdn \
--output tsv)

curl -X POST https://$ENDPOINT_FQDN/v1/completions \
-H "Content-Type: application/json" \
-d '{
    "model": "phi-3.5-mini-instruct",
    "propmpt": "Who is Inigo Montoya and from what movie?",
    "temperature": 0
}'
```