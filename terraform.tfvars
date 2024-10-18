existing_vpc_ids = [
  "vpc-02823117db1803700", 
  "vpc-0e355779798e35020"
]


region = "us-east-1"

vpc_configs = {
  "vpc" = {
    cidr_block           = "10.0.0.0/16"
    enable_dns_support   = true
    enable_dns_hostnames = true
    tags = {
      Name        = "vpc_new_1"
      Environment = "production"
    }
  }
}


#Updated terraform.tfvars
imported_vpc_configs = {
  "vpc-02823117db1803700" = {
    cidr_block = "10.0.0.0/16",
    enable_dns_support = true,
    enable_dns_hostnames = true,
    tags = {
    "Environment": "production",
    "Name": "vpc_new_terra_1"
}
  }

  "vpc-0e355779798e35020" = {
    cidr_block = "10.0.0.0/16",
    enable_dns_support = true,
    enable_dns_hostnames = true,
    tags = {
    "Environment": "Company",
    "Name": "Codincity"
}
  }

  "vpc-0ac3883de5bde45b6" = {
    cidr_block           = "172.31.0.0/16"
    enable_dns_support   = true
    enable_dns_hostnames = true
    tags = {
    "Name": "Default_VPC"
}
  }
}
