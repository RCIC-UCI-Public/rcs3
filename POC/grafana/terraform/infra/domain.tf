# domain.tf
# Simple Route 53 hosted zone logic for custom domain (prod or dev)
# - Always manages the hosted zone as a Terraform resource
# - If the zone already exists, import it with: terraform import aws_route53_zone.custom ZONE_ID

resource "aws_route53_zone" "custom" {
  name = var.domain_name
  tags = merge(local.common_tags, { Name = "${var.project_name}-${var.environment}-${var.domain_name}" })
}

# NS delegation for dev subdomain (optional, only in prod)
resource "aws_route53_record" "dev_delegation" {
  count   = length(var.dev_subdomain_name_servers) > 0 ? 1 : 0
  zone_id = aws_route53_zone.custom.zone_id
  name    = "dev" # or your subdomain prefix
  type    = "NS"
  ttl     = 300
  records = var.dev_subdomain_name_servers
}