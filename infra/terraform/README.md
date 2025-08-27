# Terraform Infra Skeleton

> AWS region defaults to **ap-south-1 (Mumbai)**. This skeleton provides:
> - A cost-safe VPC stub (VPC + public/private subnets, IGW; NAT disabled by default).
> - Two S3 buckets: **models** (versioned) and **archives** (versioned + lifecycle to Glacier/Deep Archive).
> - Parameterized variables and global tags.

## Safety
**No apply in CI.** Only `terraform fmt` and `terraform validate` are run. NAT is **off** by default to avoid accidental spend.

## Usage (local)
```bash
cd infra/terraform
terraform init -backend=false
terraform validate
```

## Naming

S3 names must be globally unique. Adjust `name_suffix` in `terraform.tfvars` before any real apply.
