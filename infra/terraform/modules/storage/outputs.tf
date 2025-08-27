output "models_bucket" {
  value = aws_s3_bucket.models.bucket
}

output "archives_bucket" {
  value = aws_s3_bucket.archives.bucket
}
