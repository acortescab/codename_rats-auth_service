locals {
  ubuntu_ami_arch = var.ami_architecture == "x86_64" ? "amd64" : "arm64"
}

data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default_vpc_subnets" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

data "aws_ami" "ubuntu_lts" {
  most_recent = true
  owners      = ["099720109477"]

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd-gp3/ubuntu-*-${var.ubuntu_lts_version}-${local.ubuntu_ami_arch}-server-*"]
  }

  filter {
    name   = "architecture"
    values = [var.ami_architecture]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  filter {
    name   = "root-device-type"
    values = ["ebs"]
  }
}
