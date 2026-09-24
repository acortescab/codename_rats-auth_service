# AGENTS.md

## Objective

Create the Terraform infrastructure required to deploy an AWS EC2 instance running **Ubuntu Linux**, with **Docker Engine** and **Docker Compose** installed and ready to run the application.

The infrastructure must be reproducible, configurable through Terraform variables, and follow AWS/Terraform best practices.

## Architecture

The infrastructure should create:

* 1 AWS EC2 instance.
* Ubuntu Server as the operating system.
* A security group for the EC2 instance.
* An IAM instance profile only if required by the application.
* Docker Engine installed on the EC2 instance.
* Docker Compose installed on the EC2 instance.
* The EC2 instance must be able to start Docker containers using `docker compose`.

Do not introduce additional AWS services unless they are explicitly required.

## Operating System

Use an official **Ubuntu Server LTS AMI**.

Do not hardcode an AMI ID because AMI IDs differ between AWS regions.

The AMI should be selected dynamically based on:

* AWS region
* Ubuntu LTS version
* Architecture

Prefer `data "aws_ami"` with filters over hardcoding an AMI ID.

Use a configurable architecture where practical, defaulting to `x86_64` unless the project explicitly requires ARM.

## EC2

Create an `aws_instance` resource.

The following values must be configurable through variables:

* AWS region
* Instance type
* Availability zone, if needed
* Root volume size
* Root volume type
* Key pair name, if SSH access is required
* Environment/name tags

Use variables rather than hardcoded infrastructure values.

The root EBS volume should:

* Use encrypted storage.
* Be configurable in size.
* Use `gp3` by default.

Example defaults:

```text
instance_type = "t3.small"
root_volume_size = 30
root_volume_type = "gp3"
```

Do not assume these defaults are appropriate for production workloads; they are development defaults.

## Networking

Do not create a complete custom VPC unless explicitly requested.

The infrastructure may use an existing/default VPC and subnet through variables or data sources.

The EC2 instance must be deployed into a subnet with internet access so it can:

* Install Docker during provisioning.
* Pull Docker images.
* Access external services when required.

Do not assign a public IP unless required by the deployment architecture.

If a public IP is required for direct access, make this configurable.

## Security Group

Create a dedicated security group for the EC2 instance.

Rules must follow least privilege.

Do not expose arbitrary ports.

SSH:

* Allow TCP port `22` only from a configurable CIDR.
* Never use `0.0.0.0/0` for SSH by default.

Application ports must be configurable.

For example:

```text
SSH      22
HTTP     80
HTTPS    443
```

Only expose ports that are actually required.

Avoid exposing database ports publicly.

## Docker Installation

Docker must be installed automatically when the EC2 instance is created.

Use the official Docker installation mechanism for Ubuntu rather than downloading random binaries.

The installation must:

1. Install required packages.
2. Install Docker Engine.
3. Install Docker CLI.
4. Install Docker Compose.
5. Enable Docker at boot.
6. Start the Docker service.
7. Add the default Ubuntu user to the `docker` group where appropriate.

After provisioning, this must work:

```bash
docker --version
docker compose version
sudo systemctl status docker
```

Docker Compose must use the modern Docker Compose V2 command:

```bash
docker compose
```

Do not install or depend on the deprecated standalone:

```bash
docker-compose
```

unless explicitly required by the project.

## Provisioning

Use EC2 `user_data` or cloud-init for initial machine provisioning.

Keep provisioning scripts maintainable.

Prefer:

```text
Terraform
   |
   +-- EC2
        |
        +-- Ubuntu
        |
        +-- cloud-init/user_data
              |
              +-- Docker
              +-- Docker Compose
```

Avoid using Terraform `remote-exec` for normal machine provisioning unless there is a specific technical reason.

The Terraform configuration should remain declarative.

## Docker Compose

Do not automatically deploy the application unless explicitly requested.

The infrastructure's responsibility is to prepare the EC2 host so that the application can later be deployed with:

```bash
docker compose up -d
```

If the project already contains a `docker-compose.yml` or `compose.yaml`, do not duplicate it inside Terraform.

Terraform should provision the host, not become the application deployment system.

## Terraform Structure

Organize Terraform into logical files.

Recommended structure:

```text
terraform/
├── main.tf
├── variables.tf
├── outputs.tf
├── providers.tf
├── versions.tf
├── data.tf
├── security_groups.tf
├── ec2.tf
├── user_data.sh
├── terraform.tfvars.example
└── README.md
```

If the project is small, some files may be combined, but avoid putting the entire infrastructure into a single large file.

## Provider

Use the official AWS Terraform provider.

Pin the provider to a compatible version range.

Also define the required Terraform version.

Do not use deprecated Terraform syntax.

## Variables

At minimum, define variables for:

```text
aws_region
instance_type
instance_name
ubuntu_version
root_volume_size
root_volume_type
ssh_allowed_cidr
key_name
enable_public_ip
```

Sensitive values must not be stored directly in Terraform files.

Use:

```text
terraform.tfvars
```

for local configuration and provide:

```text
terraform.tfvars.example
```

as a template.

Do not commit real secrets.

## Outputs

Provide useful outputs such as:

```text
instance_id
instance_private_ip
instance_public_ip
```

Only expose values that actually exist.

Do not output credentials, private keys, secrets, or sensitive configuration.

## Tags

Apply consistent tags to AWS resources.

At minimum:

```text
Name
Environment
ManagedBy
Project
```

Example:

```hcl
tags = {
  Name        = var.instance_name
  Environment = var.environment
  Project     = var.project_name
  ManagedBy   = "Terraform"
}
```

## State

Do not commit:

```text
terraform.tfstate
terraform.tfstate.*
.terraform/
```

Add them to `.gitignore`.

Do not configure a remote Terraform backend unless explicitly requested.

If a remote backend is later required, use an appropriate AWS backend and locking mechanism.

## Security Requirements

Never:

* Commit AWS credentials.
* Commit SSH private keys.
* Commit application secrets.
* Hardcode passwords.
* Hardcode API keys.
* Open SSH to the entire internet by default.
* Expose PostgreSQL publicly.
* Store secrets in `user_data`.
* Store secrets in Terraform outputs.

Remember that EC2 `user_data` can be inspected through AWS APIs and should therefore not contain long-lived secrets.

If the application requires AWS credentials, prefer an IAM instance profile/role instead of static credentials.

## Validation

Before considering the Terraform implementation complete, run:

```bash
terraform fmt -recursive
terraform validate
terraform plan
```

If AWS credentials are available, verify that `terraform plan` completes successfully.

Do not run:

```bash
terraform apply
```

unless explicitly requested.

## Expected Result

After:

```bash
terraform apply
```

the resulting EC2 instance should:

1. Run Ubuntu LTS.
2. Have Docker installed.
3. Have Docker Compose V2 installed.
4. Have Docker enabled at boot.
5. Have the Ubuntu user able to execute Docker without `sudo` after reconnecting.
6. Have only the required network ports exposed.
7. Have an encrypted EBS root volume.
8. Be fully reproducible from the Terraform configuration.

A user should be able to SSH into the instance and run:

```bash
docker --version
docker compose version
docker ps
```

successfully.
