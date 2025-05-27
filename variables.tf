variable "distribution_id" {
  description = "CloudFront Distribution ID to modify"
  type        = string
  default     = "E123456ABCDEF"
}

variable "sorry_pattern" {
  description = "Path pattern for sorry/maintenance behavior"
  type        = string
  default     = "*"
}