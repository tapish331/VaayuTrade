locals {
  tags = merge(var.tags, { Component = "storage" })
}

# MODELS bucket (versioned, encrypted)

resource "aws_s3_bucket" "models" {
  bucket = var.models_bucket_name
  tags   = merge(local.tags, { Name = var.models_bucket_name, Purpose = "models" })
}

resource "aws_s3_bucket_ownership_controls" "models" {
  bucket = aws_s3_bucket.models.id
  rule { object_ownership = "BucketOwnerEnforced" }
}

resource "aws_s3_bucket_public_access_block" "models" {
  bucket                  = aws_s3_bucket.models.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_versioning" "models" {
  bucket = aws_s3_bucket.models.id
  versioning_configuration { status = "Enabled" }
}

# Encryption: AES256 or KMS

resource "aws_s3_bucket_server_side_encryption_configuration" "models_aes" {
  count  = var.sse_kms_key_arn == null ? 1 : 0
  bucket = aws_s3_bucket.models.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "models_kms" {
  count  = var.sse_kms_key_arn == null ? 0 : 1
  bucket = aws_s3_bucket.models.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = var.sse_kms_key_arn
    }
  }
}

# ARCHIVES bucket (versioned, lifecycle to Glacier/Deep Archive, encrypted)

resource "aws_s3_bucket" "archives" {
  bucket = var.archives_bucket_name
  tags   = merge(local.tags, { Name = var.archives_bucket_name, Purpose = "archives" })
}

resource "aws_s3_bucket_ownership_controls" "archives" {
  bucket = aws_s3_bucket.archives.id
  rule { object_ownership = "BucketOwnerEnforced" }
}

resource "aws_s3_bucket_public_access_block" "archives" {
  bucket                  = aws_s3_bucket.archives.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_versioning" "archives" {
  bucket = aws_s3_bucket.archives.id
  versioning_configuration { status = "Enabled" }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "archives_aes" {
  count  = var.sse_kms_key_arn == null ? 1 : 0
  bucket = aws_s3_bucket.archives.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "archives_kms" {
  count  = var.sse_kms_key_arn == null ? 0 : 1
  bucket = aws_s3_bucket.archives.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = var.sse_kms_key_arn
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "archives" {
  bucket = aws_s3_bucket.archives.id

  rule {
    id     = "archive-tiering"
    status = "Enabled"

    transition {
      days          = var.archives_transition_days
      storage_class = "GLACIER"
    }

    transition {
      days          = var.archives_deep_archive_days
      storage_class = "DEEP_ARCHIVE"
    }

    dynamic "expiration" {
      for_each = var.archives_expiration_days > 0 ? [1] : []
      content {
        days = var.archives_expiration_days
      }
    }

  }
}
