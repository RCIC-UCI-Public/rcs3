# Local variables for resource creation conditions
locals {
  create_vpc    = var.vpc_id == ""
  create_subnet = var.subnet_id == ""
  vpc_id        = local.create_vpc ? aws_vpc.grafana[0].id : var.vpc_id
  subnet_id     = local.create_subnet ? aws_subnet.grafana[0].id : var.subnet_id
}

# VPC
resource "aws_vpc" "grafana" {
  count = local.create_vpc ? 1 : 0

  cidr_block           = var.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-${var.environment}-vpc"
  })
}

# Internet Gateway
resource "aws_internet_gateway" "grafana" {
  count = local.create_vpc ? 1 : 0

  vpc_id = aws_vpc.grafana[0].id

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-${var.environment}-igw"
  })
}

# Public Subnet
resource "aws_subnet" "grafana" {
  count = local.create_subnet ? 1 : 0

  vpc_id                  = local.vpc_id
  cidr_block              = var.subnet_cidr
  map_public_ip_on_launch = true

  # Use the first availability zone in the region
  availability_zone = data.aws_availability_zones.available.names[0]

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-${var.environment}-subnet"
  })
}

# Route Table
resource "aws_route_table" "grafana" {
  count = local.create_subnet ? 1 : 0

  vpc_id = local.vpc_id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = local.create_vpc ? aws_internet_gateway.grafana[0].id : data.aws_internet_gateway.existing[0].id
  }

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-${var.environment}-rt"
  })
}

# Route Table Association
resource "aws_route_table_association" "grafana" {
  count = local.create_subnet ? 1 : 0

  subnet_id      = aws_subnet.grafana[0].id
  route_table_id = aws_route_table.grafana[0].id
}

# Data source for availability zones
data "aws_availability_zones" "available" {
  state = "available"
}

# Data source for existing Internet Gateway (when using existing VPC)
data "aws_internet_gateway" "existing" {
  count = local.create_vpc ? 0 : 1
  filter {
    name   = "attachment.vpc-id"
    values = [var.vpc_id]
  }
}
