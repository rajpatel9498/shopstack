# 🏗️ AWS EKS Infrastructure with Terraform

This directory contains the Terraform infrastructure as code for deploying the ShopStack microservices to AWS EKS.

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        AWS EKS Infrastructure                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────┐  │
│  │   Application   │    │   Application   │    │ Application │  │
│  │   Load Balancer │    │   Load Balancer │    │ Load Balancer│  │
│  │   (Public)      │    │   (Public)      │    │ (Public)    │  │
│  └─────────────────┘    └─────────────────┘    └─────────────┘  │
│           │                       │                       │     │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                    Public Subnets                          │ │
│  │              (us-west-2a, us-west-2b, us-west-2c)          │ │
│  └─────────────────────────────────────────────────────────────┘ │
│           │                       │                       │     │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                    Private Subnets                         │ │
│  │              (us-west-2a, us-west-2b, us-west-2c)          │ │
│  └─────────────────────────────────────────────────────────────┘ │
│           │                       │                       │     │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                    EKS Cluster                             │ │
│  │                                                             │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │ │
│  │  │   Node      │  │   Node      │  │   Node      │        │ │
│  │  │   Group     │  │   Group     │  │   Group     │        │ │
│  │  │  (Worker)   │  │  (Worker)   │  │  (Worker)   │        │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘        │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────┐  │
│  │   ECR Repo      │    │   ECR Repo      │    │ ECR Repo    │  │
│  │   API Gateway   │    │   Catalog       │    │ Cart        │  │
│  └─────────────────┘    └─────────────────┘    └─────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 📁 Directory Structure

```
terraform/
├── environments/
│   └── prod/                    # Production environment
│       ├── main.tf             # Main Terraform configuration
│       ├── variables.tf         # Variable definitions
│       └── terraform.tfvars    # Variable values
├── modules/
│   ├── vpc/                    # VPC and networking module
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── eks/                    # EKS cluster module
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── ecr/                    # ECR repositories module
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   └── alb/                    # Application Load Balancer module
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
├── deploy.sh                   # Automated deployment script
└── README.md                   # This file
```

## 🚀 Quick Start

### Prerequisites

1. **AWS CLI** installed and configured
2. **Terraform** (>= 1.0) installed
3. **kubectl** installed
4. **AWS credentials** configured with appropriate permissions

### Required AWS Permissions

Your AWS user/role needs the following permissions:
- `AmazonEKSClusterPolicy`
- `AmazonEKSWorkerNodePolicy`
- `AmazonEKS_CNI_Policy`
- `AmazonEC2ContainerRegistryReadOnly`
- `AmazonVPCFullAccess`
- `AmazonElasticLoadBalancingFullAccess`
- `CloudWatchLogsFullAccess`

### Automated Deployment

1. **Run the deployment script:**
   ```bash
   cd terraform
   ./deploy.sh
   ```

2. **Follow the prompts** - the script will:
   - Check prerequisites
   - Initialize Terraform
   - Plan the deployment
   - Ask for confirmation
   - Apply the configuration
   - Configure kubectl
   - Install metrics server and cluster autoscaler

### Manual Deployment

1. **Initialize Terraform:**
   ```bash
   cd terraform/environments/prod
   terraform init
   ```

2. **Plan the deployment:**
   ```bash
   terraform plan -out=tfplan
   ```

3. **Apply the configuration:**
   ```bash
   terraform apply tfplan
   ```

4. **Configure kubectl:**
   ```bash
   aws eks update-kubeconfig --region us-west-2 --name shopstack-cluster
   ```

## 🏗️ Infrastructure Components

### **VPC Module**
- **VPC**: 10.0.0.0/16 CIDR block
- **Public Subnets**: 3 subnets across AZs for ALB
- **Private Subnets**: 3 subnets across AZs for EKS nodes
- **Internet Gateway**: For public internet access
- **NAT Gateways**: For private subnet internet access
- **Route Tables**: Proper routing for public/private subnets

### **EKS Module**
- **EKS Cluster**: Kubernetes 1.27
- **Node Groups**: Managed node groups with t3.medium instances
- **IAM Roles**: Proper permissions for cluster and nodes
- **Security Groups**: Network security for the cluster
- **Logging**: CloudWatch integration

### **ECR Module**
- **Repositories**: 3 ECR repositories for our services
- **Lifecycle Policies**: Automatic cleanup of old images
- **Image Scanning**: Security scanning on push

### **ALB Module**
- **Application Load Balancer**: Public-facing load balancer
- **Target Groups**: Health checks and routing
- **Security Groups**: Network access control
- **Listeners**: HTTP/HTTPS traffic handling

## 🔧 Configuration

### **Environment Variables**

Edit `terraform/environments/prod/terraform.tfvars` to customize:

```hcl
# AWS Region
aws_region = "us-west-2"

# EKS Cluster
cluster_name    = "shopstack-cluster"
cluster_version = "1.27"

# VPC Configuration
vpc_cidr = "10.0.0.0/16"

# Node Group Configuration
node_groups = {
  general = {
    desired_capacity = 2
    max_capacity     = 5
    min_capacity     = 1
    instance_types   = ["t3.medium"]
  }
}
```

### **Cost Optimization**

- **Instance Types**: Use spot instances for cost savings
- **Node Groups**: Scale down during low usage
- **NAT Gateways**: Consider using NAT instances for dev environments
- **Log Retention**: Adjust CloudWatch log retention periods

## 📊 Monitoring & Observability

### **CloudWatch Integration**
- **EKS Control Plane Logs**: API server, audit, authenticator logs
- **Node Group Logs**: Worker node logs
- **Custom Metrics**: Application-specific metrics

### **Cost Monitoring**
- **AWS Cost Explorer**: Track infrastructure costs
- **Resource Tagging**: Proper tagging for cost allocation
- **Budget Alerts**: Set up budget notifications

## 🔒 Security

### **Network Security**
- **Private Subnets**: EKS nodes in private subnets
- **Security Groups**: Restrictive access policies
- **NACLs**: Network access control lists

### **IAM Security**
- **Least Privilege**: Minimal required permissions
- **OIDC Provider**: For pod identity
- **IRSA**: IAM roles for service accounts

### **Container Security**
- **ECR Scanning**: Automatic vulnerability scanning
- **Image Signing**: Sign container images
- **Runtime Security**: Pod security policies

## 🧹 Cleanup

### **Destroy Infrastructure**

```bash
cd terraform/environments/prod
terraform destroy
```

⚠️ **Warning**: This will delete all AWS resources including:
- EKS cluster and node groups
- ECR repositories and images
- VPC and networking components
- Load balancers
- CloudWatch log groups

### **Cost Considerations**

- **NAT Gateways**: ~$45/month each
- **EKS Control Plane**: ~$73/month
- **EC2 Instances**: ~$30/month per t3.medium
- **ALB**: ~$16/month
- **EBS Volumes**: ~$8/month per 20GB

**Estimated Monthly Cost**: ~$200-300 for production setup

## 🚀 Next Steps

After infrastructure deployment:

1. **Push Images to ECR:**
   ```bash
   aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-west-2.amazonaws.com
   docker tag shopstack_api_gateway:latest <account>.dkr.ecr.us-west-2.amazonaws.com/shopstack-api-gateway:latest
   docker push <account>.dkr.ecr.us-west-2.amazonaws.com/shopstack-api-gateway:latest
   ```

2. **Deploy Application:**
   ```bash
   kubectl apply -f ../../ops/k8s/
   ```

3. **Configure Monitoring:**
   ```bash
   kubectl apply -f ../../ops/k8s/monitoring/
   ```

4. **Set up CI/CD:**
   - GitHub Actions for automated deployments
   - ArgoCD for GitOps workflows
   - Tekton for custom CI/CD pipelines

## 🐛 Troubleshooting

### **Common Issues**

1. **Terraform State Lock:**
   ```bash
   terraform force-unlock <lock-id>
   ```

2. **EKS Cluster Not Ready:**
   ```bash
   kubectl get nodes
   kubectl describe node <node-name>
   ```

3. **ECR Login Issues:**
   ```bash
   aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-west-2.amazonaws.com
   ```

4. **kubectl Connection Issues:**
   ```bash
   aws eks update-kubeconfig --region us-west-2 --name shopstack-cluster
   ```

### **Useful Commands**

```bash
# Check cluster status
kubectl cluster-info

# View node groups
kubectl get nodes

# Check ECR repositories
aws ecr describe-repositories

# View ALB
aws elbv2 describe-load-balancers

# Check VPC
aws ec2 describe-vpcs --filters "Name=tag:Project,Values=shopstack"
```

## 📚 Resources

- [EKS Best Practices](https://aws.amazon.com/eks/resources/best-practices/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [EKS Workshop](https://www.eksworkshop.com/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)

---

**Built with ❤️ using Terraform and AWS EKS**
