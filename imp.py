import subprocess
import hcl2
import os
import json
import boto3

def fetch_vpc_details(vpc_id):
    """Fetch VPC details from AWS using the given VPC ID."""
    ec2_client = boto3.client('ec2', region_name='us-east-1')
    response = ec2_client.describe_vpcs(VpcIds=[vpc_id])
    
    if response['Vpcs']:
        vpc = response['Vpcs'][0]
        cidr_block = vpc['CidrBlock']
        tags = {tag['Key']: tag['Value'] for tag in vpc.get('Tags', [])}
        return cidr_block, tags
    else:
        raise Exception(f"VPC with ID {vpc_id} not found.")

def vpc_exists_in_file(file_path, vpc_id):
    """Check if the VPC ID already exists in the specified file."""
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            content = f.read()
        return vpc_id in content
    return False

def append_to_tfvars(module_path, vpc_id, cidr_block, tags):
    """Append imported VPC configuration to terraform.tfvars."""
    tfvars_path = os.path.join(module_path, "terraform.tfvars")

    # Prepare new content
    new_content = f"""
imported_vpc_configs = {{
  "{vpc_id}" = {{
    cidr_block           = "{cidr_block}"
    enable_dns_support   = true
    enable_dns_hostnames = true
    tags = {json.dumps(tags, indent=4)}
  }}
}}
"""
    # Check if terraform.tfvars already has the VPC ID
    if vpc_exists_in_file(tfvars_path, vpc_id):
        print(f"VPC {vpc_id} already exists in terraform.tfvars. Skipping...")
        return

    if os.path.exists(tfvars_path):
        with open(tfvars_path, "r") as f:
            existing_content = f.read()
        
        # If the section already exists, append to it; otherwise, just add the new content
        if "imported_vpc_configs" in existing_content:
            existing_content = existing_content.replace('imported_vpc_configs = {', f'imported_vpc_configs = {{\n  "{vpc_id}" = {{\n    cidr_block = "{cidr_block}",\n    enable_dns_support = true,\n    enable_dns_hostnames = true,\n    tags = {json.dumps(tags, indent=4)}\n  }}\n')
        else:
            existing_content += new_content
        
        with open(tfvars_path, "w") as f:
            f.write(existing_content)
    else:
        with open(tfvars_path, "w") as f:
            f.write(new_content)

    print(f"Appended imported VPC {vpc_id} configuration to terraform.tfvars.")

def append_to_main_tf(module_path):
    """Append VPC resource configuration to main.tf."""
    main_tf_path = os.path.join(module_path, "main.tf")
    
    vpc_resource = """
resource "aws_vpc" "my_existing_vpc" {
  for_each = var.imported_vpc_configs
  cidr_block = each.value.cidr_block
  enable_dns_support = each.value.enable_dns_support
  enable_dns_hostnames = each.value.enable_dns_hostnames
  tags = each.value.tags
}
"""
    
    # Check if main.tf already has the VPC resource configuration
    if vpc_exists_in_file(main_tf_path, 'aws_vpc.my_existing_vpc'):
        print("VPC resource configuration already exists in main.tf. Skipping...")
        return

    if os.path.exists(main_tf_path):
        with open(main_tf_path, "a") as f:
            f.write(vpc_resource)
        print("Appended VPC resource configuration to main.tf.")
    else:
        with open(main_tf_path, "w") as f:
            f.write(vpc_resource)
        print("Created main.tf and added VPC resource configuration.")

def update_variables_tf(module_path):
    """Append imported VPC configurations to variables.tf if not exists."""
    variables_tf_path = os.path.join(module_path, "variables.tf")
    
    new_variable = """
variable "imported_vpc_configs" {
  description = "Imported VPC configurations"
  type = map(object({
    cidr_block           = string
    enable_dns_support   = bool
    enable_dns_hostnames = bool
    tags                 = map(string)
  }))
  default = {}
}
"""
    
    # Check if the variable already exists in the file
    if vpc_exists_in_file(variables_tf_path, 'variable "imported_vpc_configs"'):
        print("imported_vpc_configs variable already exists in variables.tf. Skipping...")
        return

    # Append the new variable to variables.tf
    with open(variables_tf_path, "a") as f:
        f.write(new_variable)
    print("Appended imported_vpc_configs variable to variables.tf")

def main(module_path):
    """Main function to run the script."""
    # First, read the existing VPC IDs from terraform.tfvars
    tfvars_path = os.path.join(module_path, 'terraform.tfvars')
    
    if not os.path.exists(tfvars_path):
        print("Error: terraform.tfvars file does not exist.")
        exit(1)
    
    with open(tfvars_path, 'r') as f:
        variables = hcl2.load(f)

    existing_vpc_ids = variables.get('existing_vpc_ids', [])
    
    if not existing_vpc_ids:
        print("Error: No VPC IDs found in terraform.tfvars.")
        exit(1)

    for existing_id in existing_vpc_ids:
        try:
            cidr_block, tags = fetch_vpc_details(existing_id)
        except Exception as e:
            print(f"Error fetching VPC details for {existing_id}: {e}")
            continue

        append_to_tfvars(module_path, existing_id, cidr_block, tags)

    append_to_main_tf(module_path)
    update_variables_tf(module_path)

    # Initialize Terraform
    try:
        print("Initializing Terraform...")
        subprocess.run(['terraform', 'init'], check=True)
    except subprocess.CalledProcessError as e:
        print("Error during Terraform initialization:")
        print(e.output)
        exit(1)

    # Import each VPC
    for existing_id in existing_vpc_ids:
        if vpc_exists_in_file(os.path.join(module_path, 'main.tf'), existing_id):
            print(f"VPC {existing_id} already imported. Skipping...")
            continue
        import_command = ['terraform', 'import', f'aws_vpc.my_existing_vpc["{existing_id}"]', existing_id]
        try:
            print(f"Importing VPC with ID: {existing_id}...")
            result = subprocess.run(import_command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            print("Import Output:", result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"Error during VPC import for {existing_id}:")
            print("Return code:", e.returncode)
            print("Command output:", e.output)
            print("Command error:", e.stderr)
            continue

    # Plan the changes
    try:
        print("Planning changes...")
        subprocess.run(['terraform', 'plan'], check=True)
    except subprocess.CalledProcessError as e:
        print("Error during Terraform plan:")
        print(e.output)
        exit(1)

    # Apply the changes
    try:
        print("Applying changes...")
        subprocess.run(['terraform', 'apply', '-auto-approve'], check=True)
    except subprocess.CalledProcessError as e:
        print("Error during Terraform apply:")
        print(e.output)
        exit(1)

    print("Import and VPC creation completed successfully.")

if __name__ == "__main__":
    module_path = "."  # Change this to your module path if needed
    main(module_path)
