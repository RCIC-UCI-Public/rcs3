# domain.tf
# Simple Route 53 hosted zone logic for custom domain (prod or dev)
# - Always manages the hosted zone as a Terraform resource
# - If the zone already exists, import it with: terraform import aws_route53_zone.custom ZONE_ID

resource "aws_route53_zone" "custom" {
  name = var.domain_name
  tags = merge(local.common_tags, { Name = "${var.project_name}-${var.environment}-${var.domain_name}" })
}