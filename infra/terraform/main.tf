locals {
  global_tags = merge(
    {
      Project     = var.project
      Environment = var.environment
      ManagedBy   = "terraform"
    },
    var.tags
  )
}

module "vpc" {
  source               = "./modules/vpc"
  project              = var.project
  environment          = var.environment
  vpc_cidr             = var.vpc_cidr
  az_count             = var.az_count
  public_subnet_cidrs  = var.public_subnet_cidrs
  private_subnet_cidrs = var.private_subnet_cidrs
  enable_nat_gateway   = var.enable_nat_gateway
  tags                 = local.global_tags
}

module "storage" {
  source                     = "./modules/storage"
  project                    = var.project
  environment                = var.environment
  models_bucket_name         = "${var.project}-${var.environment}-models-${var.name_suffix}"
  archives_bucket_name       = "${var.project}-${var.environment}-archives-${var.name_suffix}"
  sse_kms_key_arn            = var.s3_kms_key_arn
  archives_transition_days   = var.archives_transition_days
  archives_deep_archive_days = var.archives_deep_archive_days
  archives_expiration_days   = var.archives_expiration_days
  tags                       = local.global_tags
}
