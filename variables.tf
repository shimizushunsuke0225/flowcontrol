variable "distribution_id" {
  description = "CloudFront Distribution ID to modify"
  type        = string
  default     = "E123456ABCDEF"
}

variable "maintenance_pattern" {
  description = "Path pattern for maintenance behavior"
  type        = string
  default     = "*"
}

variable "target_priority" {
  description = "Target priority for maintenance behavior (0 for maintenance mode, 1000 for normal mode)"
  type        = string
  default     = "0"
}