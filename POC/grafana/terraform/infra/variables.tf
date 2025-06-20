# Network Configuration Variables
variable "vpc_id" {
  description = "Existing VPC ID. If not provided, a new VPC will be created"
  type        = string
  default     = ""
}

variable "subnet_id" {
  description = "Existing Subnet ID. If not provided, a new subnet will be created"
  type        = string
  default     = ""
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "172.20.0.0/16"
}

variable "subnet_cidr" {
  description = "CIDR block for subnet"
  type        = string
  default     = "172.20.1.0/24"
}

# Environment Variables
variable "environment" {
  description = "Environment name"
  type        = string
}

variable "project_name" {
  description = "Project name"
  type        = string
}

# Application Configuration
variable "grafana_admin_password" {
  description = "Grafana admin password"
  type        = string
  sensitive   = true
}

# Security Configuration
variable "allowed_cidr_blocks" {
  description = "List of CIDR blocks allowed to access Grafana"
  type        = list(string)
}

# S3 Configuration
variable "s3_bucket_name" {
  description = "Name of the S3 bucket for storing scripts and files"
  type        = string
}

# ALB Configuration
variable "use_alb" {
  description = "Whether to create an Application Load Balancer for HTTPS access"
  type        = bool
  default     = false
}
