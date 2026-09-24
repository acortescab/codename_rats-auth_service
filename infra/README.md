# Infrastructure (Terraform)

This folder provisions one Ubuntu EC2 host prepared to run Docker workloads with `docker compose`.

## What gets created

- 1 EC2 instance running Ubuntu LTS (dynamic AMI lookup by region/version/architecture)
- 1 dedicated security group (SSH + configurable app ports)
- Optional IAM role and instance profile (enabled by default)
- Encrypted root EBS volume (`gp3` by default)
- Cloud-init style host bootstrap via `user_data.sh` for Docker Engine + Compose plugin

## Prerequisites

- Terraform >= 1.5.0
- AWS credentials configured for the target account
- Existing VPC/subnet access in the target region

## Usage

1. Copy `terraform.tfvars.example` to `terraform.tfvars` and adjust values.
2. Initialize providers:

```bash
terraform init
```

3. Validate formatting and config:

```bash
terraform fmt -recursive
terraform validate
```

4. Create and review plan:

```bash
terraform plan -var-file=terraform.tfvars
```

## Notes

- If `subnet_id` is `null`, Terraform uses the first subnet from the default VPC.
- SSH is restricted to `ssh_allowed_cidr`; avoid broad CIDRs.
- Docker is installed from Docker's official Ubuntu apt repository.
- This stack prepares the host only; it does not deploy the application containers.

## Post-provision checks (on instance)

```bash
docker --version
docker compose version
sudo systemctl status docker
```
