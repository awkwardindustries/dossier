# Static Egress Gateway

Official documentation: <https://learn.microsoft.com/en-us/azure/aks/configure-static-egress-gateway>.

A static egress gateway can provide control over egress traffic at a pod level (versus in general such as the
outbound type).

## Setup Cluster and VNet

```bash
RG=EphStaticEgressLab
LOC=eastus2
CLUSTER_NAME=egresslag

az group create -n $RG -l $LOC

# Set an environment variable for the VNet name
VNET_NAME=static-egress-lab-vnet
VNET_ADDRESS_SPACE=10.140.0.0/16
AKS_SYSTEM_SUBNET_ADDRESS_SPACE=10.140.0.0/24
EGRESS_SUBNET_ADDRESS_SPACE=10.140.1.0/24

# Create the vnet
az network vnet create \
-g $RG \
-n $VNET_NAME \
--address-prefix $VNET_ADDRESS_SPACE \
--subnet-name system-subnet \
--subnet-prefix $AKS_SYSTEM_SUBNET_ADDRESS_SPACE

az network vnet subnet create \
-g $RG \
--vnet-name $VNET_NAME \
-n gateway-subnet \
--address-prefixes $EGRESS_SUBNET_ADDRESS_SPACE

# Get a subnet resource ID, which we'll need when we create the AKS cluster
SYSTEM_SUBNET_ID=$(az network vnet subnet show -g $RG --vnet-name $VNET_NAME -n system-subnet -o tsv --query id)

GATEWAY_SUBNET_ID=$(az network vnet subnet show -g $RG --vnet-name $VNET_NAME -n gateway-subnet -o tsv --query id)

az aks create \
-n $CLUSTER_NAME \
-g $RG \
--vnet-subnet-id $SYSTEM_SUBNET_ID \
--enable-static-egress-gateway

az aks get-credentials -g $RG -n $CLUSTER_NAME
```

## Setup Static Gateway Nodepool

```bash
# Add a gateway-specific nodepool
az aks nodepool add \
--cluster-name $CLUSTER_NAME \
--name gatewaypool \
--resource-group $RG \
--mode gateway \
--node-count 3 \
--gateway-prefix-size 28

# Create a namespace for our pods we'll setup to test
kubectl create ns lab

# Deploy a StaticGatewayConfiguration to the namespace
# that points to the gateway nodepool
cat <<EOF | kubectl apply -f -
apiVersion: egressgateway.kubernetes.azure.com/v1alpha1
kind: StaticGatewayConfiguration
metadata:
  name: mygwconfig
  namespace: lab
spec:
  gatewayNodepoolName: gatewaypool
EOF

# Deploy a pod specifying the egress go through the static egress gateway
cat <<EOF |kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  labels:
    run: testpod
  annotations:
        kubernetes.azure.com/static-gateway-configuration: mygwconfig
  name: testpod
  namespace: lab
spec:
  containers:
  - image: nginx
    name: testpod
  dnsPolicy: ClusterFirst
  restartPolicy: Always
EOF

# Deploy a pod with no egress specification
cat <<EOF |kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  labels:
    run: testpod2
  name: testpod2
  namespace: lab
spec:
  containers:
  - image: nginx
    name: testpod
  dnsPolicy: ClusterFirst
  restartPolicy: Always
EOF
```

## Test

```bash
# This should be the IP of the egress gateway...
kubectl exec -it testpod -n lab -- curl icanhazip.com

# This should be the IP of the standard load balancer...
kubectl exec -it testpod2 -n lab -- curl icanhazip.com
```