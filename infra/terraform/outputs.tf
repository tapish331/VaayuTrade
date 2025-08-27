output "vpc_id" {
  value       = module.vpc.vpc_id
  description = "VPC ID."
}

output "public_subnet_ids" {
  value       = module.vpc.public_subnet_ids
  description = "Public subnet IDs."
}

output "private_subnet_ids" {
  value       = module.vpc.private_subnet_ids
  description = "Private subnet IDs."
}

output "models_bucket" {
  value       = module.storage.models_bucket
  description = "Models bucket name."
}

output "archives_bucket" {
  value       = module.storage.archives_bucket
  description = "Archives bucket name."
}
