variable "project" { type = string }
variable "environment" { type = string }
variable "vpc_cidr" { type = string }
variable "az_count" { type = number }
variable "public_subnet_cidrs" { type = list(string) }
variable "private_subnet_cidrs" { type = list(string) }
variable "enable_nat_gateway" { type = bool }
variable "tags" { type = map(string) }
