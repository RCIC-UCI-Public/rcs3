# Application Load Balancer for Grafana (optional)
resource "aws_lb" "grafana" {
  count = var.use_alb ? 1 : 0
  
  name               = "${var.project_name}-${var.environment}-grafana-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.grafana_alb_sg[0].id]
  subnets            = var.subnet_id != "" ? [local.subnet_id, aws_subnet.grafana_secondary[0].id] : [aws_subnet.grafana[0].id, aws_subnet.grafana_secondary_created[0].id]

  enable_deletion_protection = false

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-${var.environment}-grafana-alb"
  })
}

# Security group for ALB (optional)
resource "aws_security_group" "grafana_alb_sg" {
  count = var.use_alb ? 1 : 0
  
  name_prefix = "${var.project_name}-${var.environment}-grafana-alb-"
  vpc_id      = local.vpc_id
  description = "Security group for Grafana ALB"

  ingress {
    description = "HTTPS from internet"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = var.allowed_cidr_blocks
  }

  ingress {
    description = "HTTP from internet (optional redirect)"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = var.allowed_cidr_blocks
  }

  egress {
    description = "All outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = local.common_tags
}

# ACM Certificate with DNS validation (optional)
resource "aws_acm_certificate" "grafana_cert" {
  count = var.use_alb && var.domain_name != "" ? 1 : 0
  
  domain_name       = "${var.grafana_subdomain}.${var.domain_name}"
  validation_method = "DNS"

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-${var.environment}-grafana-cert"
  })

  lifecycle {
    create_before_destroy = true
  }
}

# Route 53 record for ACM certificate validation (optional)
resource "aws_route53_record" "grafana_cert_validation" {
  for_each = var.use_alb && var.domain_name != "" ? {
    for dvo in aws_acm_certificate.grafana_cert[0].domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  } : {}

  allow_overwrite = true
  name            = each.value.name
  records         = [each.value.record]
  ttl             = 60
  type            = each.value.type
  zone_id         = aws_route53_zone.custom.zone_id
}

# Note: Certificate validation is automatic once DNS delegation is configured
# The certificate will validate when ACM can resolve the validation records through the delegated DNS

# Self-signed certificate for ALB (always created when ALB is used)
resource "aws_acm_certificate" "grafana_wildcard" {
  count = var.use_alb ? 1 : 0
  
  private_key      = file("${path.module}/certificates/wildcard-elb.key")
  certificate_body = file("${path.module}/certificates/wildcard-elb.crt")

  tags = merge(local.common_tags, {
    Name = "grafana-wildcard-elb-cert"
  })

  lifecycle {
    create_before_destroy = true
  }
}

# Route 53 A record for Grafana subdomain (optional)
resource "aws_route53_record" "grafana_subdomain" {
  count = var.use_alb && var.domain_name != "" ? 1 : 0

  zone_id = aws_route53_zone.custom.zone_id
  name    = "${var.grafana_subdomain}.${var.domain_name}"
  type    = "A"

  alias {
    name                   = aws_lb.grafana[0].dns_name
    zone_id                = aws_lb.grafana[0].zone_id
    evaluate_target_health = true
  }
}

# Target group for Grafana (optional)
resource "aws_lb_target_group" "grafana" {
  count = var.use_alb ? 1 : 0
  
  name     = "${var.project_name}-${var.environment}-grafana-tg"
  port     = 3000
  protocol = "HTTP"
  vpc_id   = local.vpc_id

  health_check {
    enabled             = true
    healthy_threshold   = 2
    interval            = 30
    matcher             = "200,302"
    path                = "/api/health"
    port                = "traffic-port"
    protocol            = "HTTP"
    timeout             = 5
    unhealthy_threshold = 2
  }

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-${var.environment}-grafana-tg"
  })
}

# Target group for S3 Browser (optional)
resource "aws_lb_target_group" "s3browser" {
  count = var.use_alb ? 1 : 0
  
  name     = "${var.project_name}-${var.environment}-s3browser-tg"
  port     = 3001
  protocol = "HTTP"
  vpc_id   = local.vpc_id

  health_check {
    enabled             = true
    healthy_threshold   = 2
    interval            = 30
    matcher             = "200"
    path                = "/"
    port                = "traffic-port"
    protocol            = "HTTP"
    timeout             = 5
    unhealthy_threshold = 2
  }

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-${var.environment}-s3browser-tg"
  })
}

# Attach EC2 instance to target group (optional)
resource "aws_lb_target_group_attachment" "grafana" {
  count = var.use_alb ? 1 : 0
  
  target_group_arn = aws_lb_target_group.grafana[0].arn
  target_id        = aws_instance.grafana.id
  port             = 3000
}

# Attach EC2 instance to S3 browser target group (optional)
resource "aws_lb_target_group_attachment" "s3browser" {
  count = var.use_alb ? 1 : 0
  
  target_group_arn = aws_lb_target_group.s3browser[0].arn
  target_id        = aws_instance.grafana.id
  port             = 3001
}

# HTTPS Listener with fallback certificate (optional)
# Note: Uses self-signed certificate initially, can be updated to ACM cert after validation
resource "aws_lb_listener" "grafana_https" {
  count = var.use_alb ? 1 : 0
  
  load_balancer_arn = aws_lb.grafana[0].arn
  port              = "443"
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS-1-2-2017-01"
  certificate_arn   = aws_acm_certificate.grafana_wildcard[0].arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.grafana[0].arn
  }

  tags = local.common_tags

  lifecycle {
    ignore_changes = [certificate_arn]
  }
}

# HTTP Listener (redirect to HTTPS) (optional)
resource "aws_lb_listener" "grafana_http" {
  count = var.use_alb ? 1 : 0
  
  load_balancer_arn = aws_lb.grafana[0].arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type = "redirect"

    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }

  tags = local.common_tags
}

# Listener rule for S3 browser path-based routing (optional)
resource "aws_lb_listener_rule" "s3browser" {
  count = var.use_alb ? 1 : 0
  
  listener_arn = aws_lb_listener.grafana_https[0].arn
  priority     = 100

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.s3browser[0].arn
  }

  condition {
    path_pattern {
      values = ["/s3browser*"]
    }
  }

  tags = local.common_tags
}

# Create a secondary subnet in different AZ for ALB (ALB requires 2+ AZs)
resource "aws_subnet" "grafana_secondary" {
  count = var.use_alb && var.subnet_id != "" ? 1 : 0

  vpc_id                  = local.vpc_id
  cidr_block              = cidrsubnet(data.aws_vpc.existing[0].cidr_block, 8, 2)
  availability_zone       = data.aws_availability_zones.available.names[1]
  map_public_ip_on_launch = true

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-${var.environment}-grafana-subnet-secondary"
  })
}

# Create a secondary subnet for new VPC (when creating from scratch)
resource "aws_subnet" "grafana_secondary_created" {
  count = var.use_alb && var.subnet_id == "" ? 1 : 0

  vpc_id                  = local.vpc_id
  cidr_block              = cidrsubnet(var.vpc_cidr, 8, 2)
  availability_zone       = data.aws_availability_zones.available.names[1]
  map_public_ip_on_launch = true

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-${var.environment}-grafana-subnet-secondary-created"
  })
}

# Route table association for secondary subnet (existing VPC)
resource "aws_route_table_association" "grafana_secondary" {
  count = var.use_alb && var.subnet_id != "" ? 1 : 0

  subnet_id      = aws_subnet.grafana_secondary[0].id
  route_table_id = data.aws_route_table.existing[0].id
}

# Route table association for secondary subnet (new VPC)
resource "aws_route_table_association" "grafana_secondary_created" {
  count = var.use_alb && var.subnet_id == "" ? 1 : 0

  subnet_id      = aws_subnet.grafana_secondary_created[0].id
  route_table_id = aws_route_table.grafana[0].id
}

# Data sources for existing VPC when using existing subnet
data "aws_vpc" "existing" {
  count = var.subnet_id != "" ? 1 : 0
  id    = var.vpc_id
}

data "aws_subnet" "existing" {
  count = var.subnet_id != "" ? 1 : 0
  id    = var.subnet_id
}

data "aws_route_table" "existing" {
  count     = var.subnet_id != "" ? 1 : 0
  subnet_id = var.subnet_id
}
