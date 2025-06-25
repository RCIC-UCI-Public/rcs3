# domain.tf
# Simple Route 53 hosted zone logic for custom domain (prod or dev)
# - Always manages the hosted zone as a Terraform resource
# - If the zone already exists, import it with: terraform import aws_route53_zone.custom ZONE_ID

resource "aws_route53_zone" "custom" {
  name = var.domain_name
  tags = merge(local.common_tags, { Name = "${var.project_name}-${var.environment}-${var.domain_name}" })
  delegation_set_id = var.delegation_set_id != "" ? var.delegation_set_id : null
}

# NS delegation for dev subdomain (optional, only in prod)
data "aws_route53_zone" "root" {
  count        = var.root_domain_name != "" ? 1 : 0
  name         = "${var.root_domain_name}."
  private_zone = false
}

resource "aws_route53_record" "dev_delegation" {
  count   = var.root_domain_name != "" && var.dev_delegation.subdomain != "" && length(var.dev_delegation.name_servers) > 0 ? 1 : 0
  zone_id = data.aws_route53_zone.root[0].zone_id
  name    = var.dev_delegation.subdomain
  type    = "NS"
  ttl     = 300
  records = var.dev_delegation.name_servers
}
