packer {
  required_plugins {
    amazon = {
      version = ">= 0.0.1"
      source  = "github.com/hashicorp/amazon"
    }
  }
}

variable "github_repo" {
  default = env("GITHUB_REPO_PATH")
}

variable "aws_access_key" {
  type= string
  default = env("MY_ACCESS_KEY")
}
variable "aws_secret_key" {
  type= string
  default = env("MY_SECRET_KEY")
}

variable "source_ami" {
  type    = string
  default = "ami-08c40ec9ead489470" # Ubuntu 22.04 LTS
}

variable "aws_acct_list" {
  type = list(string)
  default = ["540611298233","859657393397"]
}

variable "ssh_username" {
  type    = string
  default = "ubuntu"
}

# https://www.packer.io/plugins/builders/amazon/ebs
source "amazon-ebs" "my-ami" {
  access_key      = "${var.aws_access_key}"
  secret_key      = "${var.aws_secret_key}"
  region          = "us-east-1"
  ami_users       = "${var.aws_acct_list}"
  ami_name        = "csye6225_MySQL${formatdate("YYYY_MM_DD_hh_mm_ss", timestamp())}"
  ami_description = "AMI for CSYE 6225"
  ami_regions = [
    "us-east-1",
  ]

  aws_polling {
    delay_seconds = 120
    max_attempts  = 50
  }


  instance_type = "t2.micro"
  source_ami    = "${var.source_ami}"
  ssh_username  = "${var.ssh_username}"

  launch_block_device_mappings {
    delete_on_termination = true
    device_name           = "/dev/sda1"
    volume_size           = 50
    volume_type           = "gp2"
  }
}

build {
  sources = ["source.amazon-ebs.my-ami"]

provisioner "file"{
    source = "${var.github_repo}/Application/main.py"
    destination = "/home/ubuntu/"
  }

provisioner "file"{
    source = "${var.github_repo}/packer-ami/webapplication.service"
    destination = "/tmp/"
  }

  provisioner "shell" {
    environment_vars = [
      "DEBIAN_FRONTEND=noninteractive",
      "CHECKPOINT_DISABLE=1"
    ]
    script = "${var.github_repo}/packer-ami/scripts.sh"

  }
  }