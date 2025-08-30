# AWS Configuration
aws_region = "us-west-2"

# EKS Cluster Configuration
cluster_name    = "shopstack-cluster"
cluster_version = "1.27"

# VPC Configuration
vpc_cidr = "10.0.0.0/16"

# Availability Zones (us-west-2)
availability_zones = [
  "us-west-2a",
  "us-west-2b", 
  "us-west-2c"
]

# Private Subnets
private_subnet_cidrs = [
  "10.0.1.0/24",
  "10.0.2.0/24",
  "10.0.3.0/24"
]

# Public Subnets
public_subnet_cidrs = [
  "10.0.101.0/24",
  "10.0.102.0/24",
  "10.0.103.0/24"
]

# Environment
environment = "production"

# Common Tags
tags = {
  Project     = "shopstack"
  Environment = "production"
  ManagedBy   = "terraform"
  Owner       = "rajpatel9498"
}
