variable "grafana_url" {
  description = "URL of the Grafana instance"
  type        = string
}

variable "grafana_username" {
  description = "Username for Grafana authentication (usually 'admin')"
  type        = string
  default     = "admin"
}

variable "grafana_password" {
  description = "Admin password for Grafana authentication"
  type        = string
  sensitive   = true
}

variable "grafana_api_key" {
  description = "API Key for Grafana authentication (alternative to username/password)"
  type        = string
  sensitive   = true
  default     = null
}

variable "dashboards_path" {
  description = "Path to the dashboards JSON files"
  type        = string
  default     = "../dashboards"
}

variable "bucket_teams" {
  description = "Teams with access to specific buckets"
  type = map(object({
    email   = optional(string)
    members = list(string)
    buckets = list(string)
  }))
  default = {}
}

variable "default_user_password" {
  description = "Default password for automatically created users"
  type        = string
  default     = "ChangeMe123!" # This should be overridden in a secure way
  sensitive   = true
}

variable "admin_users" {
  description = "List of admin users to create with admin privileges"
  type        = list(string)
  default     = []
}

variable "common_dashboards" {
  description = "List of dashboard files that should be available to all users (not team-restricted)"
  type        = list(string)
  default     = ["cost-estimates.json"]
}
