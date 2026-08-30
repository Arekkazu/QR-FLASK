variable "project_name" {
  description = "Name prefix for AWS resources"
  type        = string
  default     = "qr-flask"
}

variable "aws_region" {
  description = "AWS region where resources will be created"
  type        = string
  default     = "us-east-1"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t2.micro"
}

variable "ssh_key_name" {
  description = "Existing AWS EC2 key pair name for SSH access"
  type        = string
}

variable "ssh_cidr" {
  description = "CIDR allowed for SSH (recommended: your_public_ip/32)"
  type        = string
}

variable "app_port" {
  description = "Port exposed by the Flask app (internal, behind Nginx)"
  type        = number
  default     = 5000
}

variable "app_cidr" {
  description = "CIDR allowed to reach the app port"
  type        = string
  default     = "0.0.0.0/0"
}

variable "repo_url" {
  description = "Git repository URL to clone on the EC2 instance"
  type        = string
}

variable "repo_branch" {
  description = "Git branch to deploy"
  type        = string
  default     = "deploy"
}

variable "app_user" {
  description = "Linux user that will own the application files"
  type        = string
  default     = "ec2-user"
}

# RDS
variable "db_name" {
  description = "MySQL database name"
  type        = string
  default     = "qrflask"
}

variable "db_username" {
  description = "MySQL master username"
  type        = string
  default     = "admin"
}

variable "db_password" {
  description = "MySQL master password (min 8 chars)"
  type        = string
  sensitive   = true
}

variable "db_instance_class" {
  description = "RDS instance class (free tier: db.t3.micro)"
  type        = string
  default     = "db.t3.micro"
}
