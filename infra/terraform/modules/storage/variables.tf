variable "project" { type = string }
variable "environment" { type = string }
variable "models_bucket_name" { type = string }
variable "archives_bucket_name" { type = string }
variable "sse_kms_key_arn" {
  type    = string
  default = null
}
variable "archives_transition_days" { type = number }
variable "archives_deep_archive_days" { type = number }
variable "archives_expiration_days" { type = number }
variable "tags" { type = map(string) }
