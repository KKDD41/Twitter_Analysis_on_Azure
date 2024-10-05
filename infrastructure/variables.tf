variable "resource_group_location" {
  type        = string
  default     = "australiacentral"  # It is recommended to use 'australiacentral' due Azure CPU quotas
  description = "Location of the resource group."
}

variable "admin_user_name" {
  type        = string
  default     = "<your-sample-name>"
  description = "Admin username for Azure SQL Database."
}

variable "admin_user_password" {
  type        = string
  sensitive   = true
  default     = "<your-sample-password>"
  description = "Temporary admin password for Azure SQL Database."
}

variable "environment_tag" {
    type        = string
    sensitive   = true
    default     = "Demo"
}