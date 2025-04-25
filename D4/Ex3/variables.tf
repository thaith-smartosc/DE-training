variable "resource_group_name" {
  type        = string
  description = ""
}

variable "location" {
  type        = string
  default     = "Southeast Asia"
  description = ""
}

variable "storage_account_name" {
  type        = string
  description = "Name of the Azure Storage Account (must be globally unique)"
}

variable "container_name" {
  type        = string
  default     = "datalake"
  description = "Name of the blob container"
}
