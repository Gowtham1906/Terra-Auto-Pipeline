import subprocess
import hcl2
#init
with open('terraform.tfvars', 'r') as f:
    variables = hcl2.load(f)

existing_id = variables['existing_vpc_id']

# Initialize Terraform
subprocess.run(['terraform', 'init'], check=True)

# Import the existing VPC
import_command = ['terraform', 'import', 'aws_vpc.imported_vpc', existing_id]
subprocess.run(import_command, check=True)

# Apply the new VPC creation
subprocess.run(['terraform', 'plan'], check=True)
subprocess.run(['terraform', 'apply', '-auto-approve'], check=True)

print("Import and VPC creation completed successfully.")
