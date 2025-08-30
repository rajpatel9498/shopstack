#!/bin/bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    print_error "AWS CLI is not installed. Please install it first."
    exit 1
fi

# Check if Terraform is installed
if ! command -v terraform &> /dev/null; then
    print_error "Terraform is not installed. Please install it first."
    exit 1
fi

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    print_error "kubectl is not installed. Please install it first."
    exit 1
fi

# Check AWS credentials
print_status "Checking AWS credentials..."
if ! aws sts get-caller-identity &> /dev/null; then
    print_error "AWS credentials not configured. Please run 'aws configure' first."
    exit 1
fi

AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
AWS_REGION=$(aws configure get region)
print_success "Using AWS Account: $AWS_ACCOUNT_ID, Region: $AWS_REGION"

# Navigate to the Terraform directory
cd environments/prod

# Initialize Terraform
print_status "Initializing Terraform..."
terraform init

# Plan the deployment
print_status "Planning Terraform deployment..."
terraform plan -out=tfplan

# Ask for confirmation
echo
print_warning "This will create the following AWS resources:"
echo "  - VPC with public and private subnets"
echo "  - EKS cluster with managed node groups"
echo "  - ECR repositories for container images"
echo "  - Application Load Balancer"
echo "  - CloudWatch log groups"
echo
read -p "Do you want to proceed with the deployment? (y/N): " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_warning "Deployment cancelled."
    exit 0
fi

# Apply the Terraform configuration
print_status "Applying Terraform configuration..."
terraform apply tfplan

# Get cluster info
print_status "Getting EKS cluster information..."
CLUSTER_NAME=$(terraform output -raw cluster_name 2>/dev/null || echo "shopstack-cluster")
CLUSTER_ENDPOINT=$(terraform output -raw cluster_endpoint)
CLUSTER_CA_DATA=$(terraform output -raw cluster_certificate_authority_data)

# Update kubeconfig
print_status "Updating kubeconfig..."
aws eks update-kubeconfig --region $AWS_REGION --name $CLUSTER_NAME

# Wait for cluster to be ready
print_status "Waiting for EKS cluster to be ready..."
kubectl wait --for=condition=ready nodes --all --timeout=300s

# Install metrics server
print_status "Installing metrics server..."
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# Install cluster autoscaler
print_status "Installing cluster autoscaler..."
kubectl apply -f https://raw.githubusercontent.com/kubernetes/autoscaler/master/cluster-autoscaler/cloudprovider/aws/examples/cluster-autoscaler-autodiscover.yaml

# Patch cluster autoscaler deployment
kubectl patch deployment cluster-autoscaler \
  -n kube-system \
  -p '{"spec":{"template":{"metadata":{"annotations":{"cluster-autoscaler.kubernetes.io/safe-to-evict": "false"}}}}}'

# Get ECR repository URLs
print_status "Getting ECR repository information..."
ECR_REPOS=$(terraform output -raw ecr_repository_urls)

print_success "Deployment completed successfully!"
echo
echo "=== Deployment Summary ==="
echo "EKS Cluster: $CLUSTER_NAME"
echo "Cluster Endpoint: $CLUSTER_ENDPOINT"
echo "ECR Repositories:"
echo "$ECR_REPOS" | tr ' ' '\n'
echo
echo "=== Next Steps ==="
echo "1. Push your Docker images to ECR:"
echo "   aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"
echo
echo "2. Deploy your application:"
echo "   kubectl apply -f ../../ops/k8s/"
echo
echo "3. Access your application:"
echo "   kubectl get svc -n shopstack"
echo
print_success "AWS EKS infrastructure is ready!"
