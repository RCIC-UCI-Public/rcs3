# Security group for Grafana EC2 instance (works in conjunction with subnet NACLs)
resource "aws_security_group" "grafana_sg" {
  name_prefix = "${var.project_name}-${var.environment}-grafana-"
  vpc_id      = local.vpc_id
  description = "Instance-level security for Grafana (requires compatible subnet NACLs)"


  ingress {
    description = "Grafana Web Interface (requires NACL permission)"
    from_port   = 3000
    to_port     = 3000
    protocol    = "tcp"
    cidr_blocks = var.allowed_cidr_blocks
  }

  ingress {
    description = "S3 Browser Web Interface (requires NACL permission)"
    from_port   = 3001
    to_port     = 3001
    protocol    = "tcp"
    cidr_blocks = var.allowed_cidr_blocks
  }


  egress {
    description = "All outbound traffic (requires NACL permission for specific ports)"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = local.common_tags
}

# IAM role for Grafana EC2 instance
resource "aws_iam_role" "grafana_role" {
  name = "${var.project_name}-${var.environment}-grafana-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })

  tags = local.common_tags
}

# Policy for CloudWatch and Systems Manager access
resource "aws_iam_role_policy" "grafana_access_policy" {
  name = "${var.project_name}-${var.environment}-grafana-access-policy"
  role = aws_iam_role.grafana_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          # CloudWatch Permissions
          "cloudwatch:GetMetricData",
          "cloudwatch:ListMetrics",
          "cloudwatch:GetMetricStatistics",
          "cloudwatch:GetMetricStream",
          "cloudwatch:ListMetricStreams",
          "cloudwatch:GetDashboard",
          "cloudwatch:ListDashboards",
          "cloudwatch:GetInsightRules",
          "cloudwatch:DescribeAlarmsForMetric",
          "cloudwatch:ListTagsForResource",
          # CloudWatch Logs Permissions
          "logs:StartQuery",
          "logs:StopQuery",
          "logs:GetQueryResults",
          "logs:GetLogEvents",
          "logs:DescribeLogGroups",
          "logs:DescribeLogStreams",
          # EC2 Permissions
          "ec2:DescribeRegions",
          # OAM Permissions
          "oam:ListSinks",
          # S3 Storage Lens Permissions
          "s3:GetStorageLensConfiguration",
          "s3:ListStorageLensConfigurations",
          "s3:GetStorageLensConfigurationTagging",
          "s3:GetStorageLensDashboard",
          "s3:GetAccountPublicAccessBlock",
          "s3:ListAllMyBuckets",
          "s3:GetBucketLocation",
          # S3 Browser Read-only Permissions
          "s3:ListBucket",
          "s3:ListBucketVersions",
          "s3:GetObject",
          "s3:GetObjectAttributes",
          "s3:GetBucketVersioning",
          "s3:GetBucketAcl",
          "s3:GetBucketPolicy",
          "s3:GetBucketTagging",
          # General Permissions
          "tag:GetResources"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "ec2:DescribeInstances",
          "ssm:DescribeAssociation",
          "ssm:GetDeployablePatchSnapshotForInstance",
          "ssm:GetDocument",
          "ssm:DescribeDocument",
          "ssm:GetManifest",
          "ssm:GetParameters",
          "ssm:ListAssociations",
          "ssm:ListInstanceAssociations",
          "ssm:PutInventory",
          "ssm:PutComplianceItems",
          "ssm:PutConfigurePackageResult",
          "ssm:UpdateAssociationStatus",
          "ssm:UpdateInstanceAssociationStatus",
          "ssm:UpdateInstanceInformation",
          "ssmmessages:CreateControlChannel",
          "ssmmessages:CreateDataChannel",
          "ssmmessages:OpenControlChannel",
          "ssmmessages:OpenDataChannel",
          "ec2messages:AcknowledgeMessage",
          "ec2messages:DeleteMessage",
          "ec2messages:FailMessage",
          "ec2messages:GetEndpoint",
          "ec2messages:GetMessages",
          "ec2messages:SendReply"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject"
        ]
        Resource = [
          "arn:aws:s3:::rcs3-godfather-uci-p-bucket/scripts/*"
        ]
      }
    ]
  })
}

# Instance profile
resource "aws_iam_instance_profile" "grafana_profile" {
  name = "${var.project_name}-${var.environment}-grafana-profile"
  role = aws_iam_role.grafana_role.name
}

# Get latest Ubuntu 20.04 LTS AMI
data "aws_ami" "ubuntu" {
  most_recent = true

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  owners = ["099720109477"] # Canonical
}

# Upload install script to S3
resource "aws_s3_object" "install_script" {
  bucket = "rcs3-godfather-uci-p-bucket"
  key    = "scripts/install-grafana-s3browser.sh"
  source = "${path.module}/install-grafana-s3browser.sh"
  etag   = filemd5("${path.module}/install-grafana-s3browser.sh")

  tags = local.common_tags
}

# Upload S3 browser source files to S3
resource "aws_s3_object" "s3_browser_server" {
  bucket = "rcs3-godfather-uci-p-bucket"
  key    = "s3-browser/server.js"
  source = "${path.module}/../../s3-browser-proxy/server.js"
  etag   = filemd5("${path.module}/../../s3-browser-proxy/server.js")

  tags = local.common_tags
}

resource "aws_s3_object" "s3_browser_package_json" {
  bucket = "rcs3-godfather-uci-p-bucket"
  key    = "s3-browser/package.json"
  source = "${path.module}/../../s3-browser-proxy/package.json"
  etag   = filemd5("${path.module}/../../s3-browser-proxy/package.json")

  tags = local.common_tags
}

resource "aws_s3_object" "s3_browser_index_html" {
  bucket = "rcs3-godfather-uci-p-bucket"
  key    = "s3-browser/public/index.html"
  source = "${path.module}/../../s3-browser-proxy/public/index.html"
  etag   = filemd5("${path.module}/../../s3-browser-proxy/public/index.html")

  tags = local.common_tags
}


# EC2 instance for Grafana
resource "aws_instance" "grafana" {
  ami                                  = data.aws_ami.ubuntu.id
  instance_type                        = "t2.micro"
  subnet_id                            = local.subnet_id
  instance_initiated_shutdown_behavior = "stop"
  monitoring                           = true
  associate_public_ip_address          = true

  vpc_security_group_ids = [aws_security_group.grafana_sg.id]
  iam_instance_profile   = aws_iam_instance_profile.grafana_profile.name

  root_block_device {
    volume_size = 20
    volume_type = "gp3"
    encrypted   = true
  }

  credit_specification {
    cpu_credits = "standard"
  }

  user_data = base64encode(<<-EOF
#!/bin/bash
set -e

# Update system
apt-get update

# Install required packages
apt-get install -y unzip curl

# Install AWS CLI v2
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
./aws/install

# Install/Update SSM Agent for Session Manager
snap refresh amazon-ssm-agent || snap install amazon-ssm-agent --classic
systemctl enable snap.amazon-ssm-agent.amazon-ssm-agent.service
systemctl start snap.amazon-ssm-agent.amazon-ssm-agent.service

# Download and execute the install script from S3
aws s3 cp s3://rcs3-godfather-uci-p-bucket/scripts/install-grafana-s3browser.sh /tmp/install-script.sh
chmod +x /tmp/install-script.sh

# Set environment variable for Grafana admin password
export GRAFANA_ADMIN_PASSWORD="${var.grafana_admin_password}"

# Execute the script
/tmp/install-script.sh

# Clean up
rm -f /tmp/install-script.sh awscliv2.zip
rm -rf aws/
EOF
  )

  depends_on = [
    aws_s3_object.install_script,
    aws_s3_object.s3_browser_server,
    aws_s3_object.s3_browser_package_json,
    aws_s3_object.s3_browser_index_html
  ]

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-${var.environment}-grafana"
    },
    {
      "ProtectionLevel" = "P1P2"
  })
}
