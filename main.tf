provider "aws" {
  region  = var.region
}

resource "aws_vpc" "my_vpc" {
  for_each = var.vpc_configs 
  
  cidr_block           = each.value.cidr_block
  enable_dns_support   = each.value.enable_dns_support
  enable_dns_hostnames = each.value.enable_dns_hostnames
  tags                 = each.value.tags
}

# terraform {
#   backend "s3" {
#     bucket = "my-infra-bucket-161024"
#     key    = "terraform/statefile.tfstate"
#     region = "us-east-1" 
#   }
# }


resource "aws_vpc" "my_existing_vpc" {
  for_each = var.imported_vpc_configs
  cidr_block = each.value.cidr_block
  enable_dns_support = each.value.enable_dns_support
  enable_dns_hostnames = each.value.enable_dns_hostnames
  tags = each.value.tags
}
