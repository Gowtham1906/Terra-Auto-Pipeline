existing_vpc_ids = [
  "vpc-0ac3883de5bde45b6", 
  "vpc-01b03447d299d032d"
]

region = "us-east-1"

vpc_configs = {
  "vpc" = {
    cidr_block           = "10.0.0.0/16"
    enable_dns_support   = true
    enable_dns_hostnames = true
    tags = {
      Name        = "vpc_new"
      Environment = "production"
    }
  }
}
