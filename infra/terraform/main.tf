data "aws_ssm_parameter" "amazon_linux_2023_ami" {
  name = "/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64"
}

locals {
  deploy_path = "/opt/${var.project_name}"
}

# ── VPC ──────────────────────────────────────────────────────────────────────

resource "aws_vpc" "main" {
  cidr_block           = "10.20.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true
  tags = { Name = "${var.project_name}-vpc" }
}

resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.20.1.0/24"
  availability_zone       = "${var.aws_region}a"
  map_public_ip_on_launch = true
  tags = { Name = "${var.project_name}-public-subnet" }
}

# Subnets privadas para RDS (requiere mínimo 2 AZs)
resource "aws_subnet" "private_a" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.20.2.0/24"
  availability_zone = "${var.aws_region}a"
  tags = { Name = "${var.project_name}-private-subnet-a" }
}

resource "aws_subnet" "private_b" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.20.3.0/24"
  availability_zone = "${var.aws_region}b"
  tags = { Name = "${var.project_name}-private-subnet-b" }
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
  tags   = { Name = "${var.project_name}-igw" }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }
  tags = { Name = "${var.project_name}-public-rt" }
}

resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}

# ── Security Groups ───────────────────────────────────────────────────────────

resource "aws_security_group" "ec2" {
  name        = "${var.project_name}-ec2-sg"
  description = "Security group for QR Flask EC2"
  vpc_id      = aws_vpc.main.id

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.ssh_cidr]
  }

  ingress {
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTP redirect"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { Name = "${var.project_name}-ec2-sg" }
}

# resource "aws_security_group" "rds" {
#   name        = "${var.project_name}-rds-sg"
#   description = "Allow MySQL from EC2 only"
#   vpc_id      = aws_vpc.main.id
# 
#   ingress {
#     description     = "MySQL from EC2"
#     from_port       = 3306
#     to_port         = 3306
#     protocol        = "tcp"
#     security_groups = [aws_security_group.ec2.id]
#   }
# 
#   egress {
#     from_port   = 0
#     to_port     = 0
#     protocol    = "-1"
#     cidr_blocks = ["0.0.0.0/0"]
#   }
# 
#   tags = { Name = "${var.project_name}-rds-sg" }
# }

# ── RDS MySQL ─────────────────────────────────────────────────────────────────

# resource "aws_db_subnet_group" "main" {
#   name       = "${var.project_name}-db-subnet-group"
#   subnet_ids = [aws_subnet.private_a.id, aws_subnet.private_b.id]
#   tags       = { Name = "${var.project_name}-db-subnet-group" }
# }
# 
# resource "aws_db_instance" "mysql" {
#   identifier             = "${var.project_name}-db"
#   engine                 = "mysql"
#   engine_version         = "8.0"
#   instance_class         = var.db_instance_class
#   allocated_storage      = 20
#   db_name                = var.db_name
#   username               = var.db_username
#   password               = var.db_password
#   db_subnet_group_name   = aws_db_subnet_group.main.name
#   vpc_security_group_ids = [aws_security_group.rds.id]
#   publicly_accessible    = false
#   skip_final_snapshot    = true
#   multi_az               = false
# 
#   tags = { Name = "${var.project_name}-db" }
# }

# ── EC2 ───────────────────────────────────────────────────────────────────────

resource "aws_instance" "app" {
  ami                         = data.aws_ssm_parameter.amazon_linux_2023_ami.value
  instance_type               = var.instance_type
  subnet_id                   = aws_subnet.public.id
  key_name                    = var.ssh_key_name
  vpc_security_group_ids      = [aws_security_group.ec2.id]
  associate_public_ip_address = true

  user_data = templatefile("${path.module}/user_data.sh.tftpl", {
    project_name = var.project_name
    app_port     = var.app_port
    repo_url     = var.repo_url
    repo_branch  = var.repo_branch
    deploy_path  = local.deploy_path
    app_user     = var.app_user
    db_url       = "sqlite:///${local.deploy_path}/instance/app.db"
  })

  # depends_on = [aws_db_instance.mysql]

  tags = { Name = "${var.project_name}-ec2" }
}
