provider "aws" {
  region = "us-east-1"  # Replace with your desired region
}

resource "aws_vpc" "imported_vpc" {
lifecycle {
    ignore_changes = [
      tags,
    ]
  }
}

resource "aws_vpc" "new_vpc" {
  cidr_block = var.cidr_block
  enable_dns_support = true
  enable_dns_hostnames = true
  tags = {
    Name = var.vpc_name
  }
}
