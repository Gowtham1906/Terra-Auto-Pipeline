import subprocess
import hcl2
 
# Load variables from the terraform.tfvars file
with open('terraform.tfvars', 'r') as f:
    variables = hcl2.load(f)
 
existing_id = variables['existing_vpc_id']
 
# Initialize Terraform
try:
    print("Initializing Terraform...")
    subprocess.run(['terraform', 'init'], check=True)
except subprocess.CalledProcessError as e:
    print("Error during Terraform initialization:")
    print(e.output)
    exit(1)
 
# Import the existing VPC
import_command = ['terraform', 'import', 'aws_vpc.imported_vpc', existing_id]
try:
    print(f"Importing VPC with ID: {existing_id}...")
    result = subprocess.run(import_command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    print("Import Output:", result.stdout)
except subprocess.CalledProcessError as e:
    print("Error during VPC import:")
    print("Return code:", e.returncode)
    print("Command output:", e.output)
    print("Command error:", e.stderr)
    exit(1)
 
# Plan the new VPC creation
try:
    print("Planning new VPC creation...")
    subprocess.run(['terraform', 'plan'], check=True)
except subprocess.CalledProcessError as e:
    print("Error during Terraform plan:")
    print(e.output)
    exit(1)
 
# Apply the new VPC creation
try:
    print("Applying new VPC creation...")
    subprocess.run(['terraform', 'apply', '-auto-approve'], check=True)
except subprocess.CalledProcessError as e:
    print("Error during Terraform apply:")
    print(e.output)
    exit(1)
 
print("Import and VPC creation completed successfully.")
