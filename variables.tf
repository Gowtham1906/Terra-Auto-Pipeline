variable "existing_vpc_id" {
  description = "The ID of the existing VPC to import"
  type        = string
}

variable "vpc_name" {
  description = "The name of the new VPC to be created"
  type        = string
}

variable "cidr_block" {
  description = "CIDR block for the new VPC"
  type        = string
}
