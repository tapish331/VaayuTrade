variable "project" {
  description = "Project slug used in names and tags."
  type        = string
  default     = "vaayutrade"
}

variable "environment" {
  description = "Deployment environment."
  type        = string
  default     = "dev"
  validation {
    condition     = contains(["dev", "stage", "prod"], var.environment)
    error_message = "environment must be one of dev, stage, prod."
  }
}

variable "region" {
  description = "AWS region."
  type        = string
  default     = "ap-south-1"
}

variable "name_suffix" {
  description = "A short, human-set suffix to keep bucket names globally-unique (e.g., your initials)."
  type        = string
  default     = "local"
}

variable "tags" {
  description = "Additional tags to apply to all resources."
  type        = map(string)
  default     = {}
}

# VPC parameters (cost-safe stub)
variable "vpc_cidr" {
  description = "VPC CIDR."
  type        = string
  default     = "10.20.0.0/16"
}

variable "az_count" {
  description = "How many AZs to spread subnets across."
  type        = number
  default     = 2
}

variable "public_subnet_cidrs" {
  description = "CIDRs for public subnets."
  type        = list(string)
  default     = ["10.20.0.0/24", "10.20.1.0/24"]
}

variable "private_subnet_cidrs" {
  description = "CIDRs for private subnets."
  type        = list(string)
  default     = ["10.20.10.0/24", "10.20.11.0/24"]
}

variable "enable_nat_gateway" {
  description = "Create a NAT Gateway (costs $$). Default off."
  type        = bool
  default     = false
}

# Storage parameters
variable "s3_kms_key_arn" {
  description = "Optional KMS key ARN for bucket encryption; if null, use SSE-S3 (AES256)."
  type        = string
  default     = null
}

variable "archives_transition_days" {
  description = "Days before transitioning archives to GLACIER."
  type        = number
  default     = 30
}

variable "archives_deep_archive_days" {
  description = "Days before transitioning archives to DEEP_ARCHIVE."
  type        = number
  default     = 180
}

variable "archives_expiration_days" {
  description = "Expire archived objects after N days (e.g., 3 years = 1095). Set 0 to disable."
  type        = number
  default     = 1095
}
