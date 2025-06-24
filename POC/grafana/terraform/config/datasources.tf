resource "grafana_data_source" "cloudwatch" {
  name = "CloudWatch"
  type = "cloudwatch"

  json_data_encoded = jsonencode({
    authType                = "default"
    defaultRegion           = "us-west-2"
    customMetricsNamespaces = "AWS/S3/Storage-Lens,rcs3"
  })
}
