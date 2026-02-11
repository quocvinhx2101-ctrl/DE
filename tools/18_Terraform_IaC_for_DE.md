# 🏗️ Terraform & Infrastructure as Code cho DE

> Mọi thứ trong code. Reproducible. Reviewable. Versioned.

---

## 📋 Mục Lục

1. [Tại Sao DE Cần IaC?](#tại-sao-de-cần-iac)
2. [Terraform Basics](#terraform-basics)
3. [DE Infrastructure Patterns](#de-infrastructure-patterns)
4. [Modules cho Data Pipelines](#modules-cho-data-pipelines)
5. [State Management](#state-management)
6. [CI/CD cho Infrastructure](#cicd-cho-infrastructure)
7. [Alternatives](#alternatives)

---

## Tại Sao DE Cần IaC?

### Không Có IaC

```
Manual setup:
1. Click through AWS Console → Create S3 bucket
2. Click through → Create Glue catalog
3. Click through → Create Redshift cluster
4. Click through → Setup IAM roles
5. Click through → Configure networking

Problems:
- Forget a step → Production broken
- Colleague asks "how did you set this up?" → "Uhhh..."
- Need same infra in staging → Spend 2 days clicking
- Audit: "Who changed the security group?" → No record
```

### Có IaC

```
Everything in code:
1. Write Terraform → git commit → PR review → apply
2. Need staging? → terraform workspace new staging → apply
3. Who changed what? → git log
4. Disaster recovery? → terraform apply (recreate everything)
```

---

## Terraform Basics

### Core Concepts

```
Terraform workflow:
Write → Plan → Apply

write:  Define infrastructure in .tf files
plan:   terraform plan → Preview changes
apply:  terraform apply → Create/update resources
```

### First DE Infrastructure

```hcl
# main.tf — Simple data pipeline infrastructure

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.region
}

# Variables
variable "region" {
  default = "ap-southeast-1"  # Singapore (gần VN)
}

variable "environment" {
  default = "dev"
}

variable "project_name" {
  default = "data-pipeline"
}

# S3 Bucket for Data Lake
resource "aws_s3_bucket" "data_lake" {
  bucket = "${var.project_name}-${var.environment}-data-lake"
  
  tags = {
    Environment = var.environment
    Project     = var.project_name
    ManagedBy   = "terraform"
  }
}

resource "aws_s3_bucket_versioning" "data_lake" {
  bucket = aws_s3_bucket.data_lake.id
  versioning_configuration {
    status = "Enabled"
  }
}

# Lifecycle rule: move old data to cheaper storage
resource "aws_s3_bucket_lifecycle_configuration" "data_lake" {
  bucket = aws_s3_bucket.data_lake.id

  rule {
    id     = "archive-old-data"
    status = "Enabled"

    transition {
      days          = 90
      storage_class = "STANDARD_IA"
    }

    transition {
      days          = 365
      storage_class = "GLACIER"
    }
  }
}
```

### Data Lake Structure

```hcl
# S3 bucket structure for Medallion architecture
locals {
  data_lake_folders = [
    "bronze/",      # Raw data
    "silver/",      # Cleaned data
    "gold/",        # Aggregated data
    "staging/",     # Temporary staging
    "archive/",     # Old data
    "scripts/",     # ETL scripts
    "configs/",     # Configuration files
  ]
}

resource "aws_s3_object" "data_lake_folders" {
  for_each = toset(local.data_lake_folders)
  
  bucket = aws_s3_bucket.data_lake.id
  key    = each.value
}
```

### Database Resources

```hcl
# RDS PostgreSQL for metadata/operational data
resource "aws_db_instance" "metadata_db" {
  identifier     = "${var.project_name}-${var.environment}-metadata"
  engine         = "postgres"
  engine_version = "15.4"
  instance_class = var.environment == "prod" ? "db.r6g.large" : "db.t3.small"
  
  allocated_storage     = 100
  max_allocated_storage = 500  # Auto-scale
  storage_encrypted     = true
  
  db_name  = "pipeline_metadata"
  username = "admin"
  password = var.db_password  # From secrets manager
  
  vpc_security_group_ids = [aws_security_group.db.id]
  db_subnet_group_name   = aws_db_subnet_group.db.name
  
  backup_retention_period = 7
  multi_az               = var.environment == "prod" ? true : false
  
  skip_final_snapshot = var.environment != "prod"
  
  tags = {
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

# Redshift Serverless for warehouse
resource "aws_redshiftserverless_namespace" "warehouse" {
  namespace_name = "${var.project_name}-${var.environment}"
  admin_username = "admin"
  admin_user_password = var.redshift_password
  db_name        = "warehouse"
}

resource "aws_redshiftserverless_workgroup" "warehouse" {
  namespace_name = aws_redshiftserverless_namespace.warehouse.namespace_name
  workgroup_name = "${var.project_name}-${var.environment}-wg"
  base_capacity  = var.environment == "prod" ? 128 : 32  # RPUs
}
```

---

## DE Infrastructure Patterns

### Pattern 1: Complete Airflow Setup

```hcl
# MWAA (Managed Airflow) on AWS
resource "aws_mwaa_environment" "airflow" {
  name = "${var.project_name}-${var.environment}-airflow"
  
  airflow_version   = "2.8.1"
  environment_class = var.environment == "prod" ? "mw1.medium" : "mw1.small"
  
  dag_s3_path          = "dags/"
  requirements_s3_path = "requirements.txt"
  
  source_bucket_arn = aws_s3_bucket.airflow.arn
  
  execution_role_arn = aws_iam_role.airflow.arn
  
  network_configuration {
    security_group_ids = [aws_security_group.airflow.id]
    subnet_ids         = var.private_subnet_ids
  }
  
  logging_configuration {
    dag_processing_logs {
      enabled   = true
      log_level = "INFO"
    }
    scheduler_logs {
      enabled   = true
      log_level = "WARNING"
    }
    task_logs {
      enabled   = true
      log_level = "INFO"
    }
  }
  
  max_workers = var.environment == "prod" ? 10 : 2
  min_workers = 1
}
```

### Pattern 2: Kafka Cluster

```hcl
# MSK (Managed Kafka) on AWS
resource "aws_msk_cluster" "kafka" {
  cluster_name           = "${var.project_name}-${var.environment}"
  kafka_version          = "3.6.0"
  number_of_broker_nodes = var.environment == "prod" ? 6 : 3
  
  broker_node_group_info {
    instance_type   = var.environment == "prod" ? "kafka.m5.2xlarge" : "kafka.t3.small"
    client_subnets  = var.private_subnet_ids
    security_groups = [aws_security_group.kafka.id]
    
    storage_info {
      ebs_storage_info {
        volume_size = var.environment == "prod" ? 1000 : 100
      }
    }
  }
  
  encryption_info {
    encryption_in_transit {
      client_broker = "TLS"
      in_cluster    = true
    }
  }
  
  configuration_info {
    arn      = aws_msk_configuration.kafka.arn
    revision = aws_msk_configuration.kafka.latest_revision
  }
}

resource "aws_msk_configuration" "kafka" {
  name = "${var.project_name}-config"
  
  server_properties = <<PROPERTIES
auto.create.topics.enable=false
default.replication.factor=3
min.insync.replicas=2
num.partitions=12
log.retention.hours=168
PROPERTIES
}
```

### Pattern 3: Spark/EMR

```hcl
# EMR Serverless for Spark
resource "aws_emrserverless_application" "spark" {
  name          = "${var.project_name}-${var.environment}-spark"
  release_label = "emr-7.0.0"
  type          = "spark"
  
  maximum_capacity {
    cpu    = var.environment == "prod" ? "400 vCPU" : "40 vCPU"
    memory = var.environment == "prod" ? "3000 GB" : "300 GB"
  }
  
  auto_start_configuration {
    enabled = true
  }
  
  auto_stop_configuration {
    enabled              = true
    idle_timeout_minutes = 15
  }
  
  initial_capacity {
    initial_capacity_type = "Driver"
    initial_capacity_config {
      worker_count = 1
      worker_configuration {
        cpu    = "4 vCPU"
        memory = "16 GB"
      }
    }
  }
}
```

---

## Modules cho Data Pipelines

### Reusable S3 Data Lake Module

```hcl
# modules/data-lake/main.tf
variable "name" {}
variable "environment" {}
variable "enable_versioning" { default = true }
variable "lifecycle_glacier_days" { default = 365 }

resource "aws_s3_bucket" "this" {
  bucket = "${var.name}-${var.environment}"
}

resource "aws_s3_bucket_versioning" "this" {
  count  = var.enable_versioning ? 1 : 0
  bucket = aws_s3_bucket.this.id
  versioning_configuration { status = "Enabled" }
}

output "bucket_name" { value = aws_s3_bucket.this.bucket }
output "bucket_arn" { value = aws_s3_bucket.this.arn }

# Usage:
# module "data_lake" {
#   source      = "./modules/data-lake"
#   name        = "company-data-lake"
#   environment = "prod"
# }
```

---

## State Management

### Remote State (Required for Team)

```hcl
# backend.tf
terraform {
  backend "s3" {
    bucket         = "company-terraform-state"
    key            = "data-platform/terraform.tfstate"
    region         = "ap-southeast-1"
    dynamodb_table = "terraform-lock"
    encrypt        = true
  }
}

# DynamoDB for state locking (prevent concurrent applies)
resource "aws_dynamodb_table" "terraform_lock" {
  name         = "terraform-lock"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"
  
  attribute {
    name = "LockID"
    type = "S"
  }
}
```

### Workspaces for Environments

```bash
# Create environments
terraform workspace new dev
terraform workspace new staging
terraform workspace new prod

# Switch between environments
terraform workspace select prod

# Use in config
# instance_class = terraform.workspace == "prod" ? "db.r6g.large" : "db.t3.small"
```

---

## CI/CD cho Infrastructure

### GitHub Actions Pipeline

```yaml
# .github/workflows/terraform.yml
name: Terraform Pipeline

on:
  pull_request:
    paths: ['infra/**']
  push:
    branches: [main]
    paths: ['infra/**']

jobs:
  plan:
    runs-on: ubuntu-latest
    if: github.event_name == 'pull_request'
    steps:
      - uses: actions/checkout@v4
      - uses: hashicorp/setup-terraform@v3
      
      - name: Terraform Init
        run: terraform init
        working-directory: infra/
      
      - name: Terraform Plan
        run: terraform plan -no-color -out=plan.tfplan
        working-directory: infra/
      
      - name: Comment Plan on PR
        uses: actions/github-script@v7
        with:
          script: |
            const plan = `terraform plan output here`;
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: '```\n' + plan + '\n```'
            });

  apply:
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    steps:
      - uses: actions/checkout@v4
      - uses: hashicorp/setup-terraform@v3
      
      - name: Terraform Init
        run: terraform init
        working-directory: infra/
      
      - name: Terraform Apply
        run: terraform apply -auto-approve
        working-directory: infra/
```

---

## Alternatives

| Tool | Best For | Language |
|------|----------|---------|
| **Terraform** | Multi-cloud, general purpose | HCL |
| **Pulumi** | Developer-friendly, real programming | Python/Go/TS |
| **CDK (AWS)** | AWS-only, TypeScript/Python | TS/Python |
| **CloudFormation** | AWS-only, YAML/JSON | YAML |
| **Crossplane** | Kubernetes-native | YAML |

---

## Checklist

- [ ] Hiểu IaC benefits cho DE
- [ ] Viết được basic Terraform cho S3, RDS, networking
- [ ] Biết dùng modules cho reusability
- [ ] Setup remote state & locking
- [ ] CI/CD pipeline cho Terraform (plan on PR, apply on merge)
- [ ] Biết tạo environments (dev/staging/prod) bằng workspaces

---

## Liên Kết

- [10_Cloud_Platforms](../fundamentals/10_Cloud_Platforms.md) - Cloud services
- [16_DE_Environment_Setup](../fundamentals/16_DE_Environment_Setup.md) - Docker, local setup
- [11_Testing_CICD](../fundamentals/11_Testing_CICD.md) - CI/CD practices

---

*Nếu bạn không thể recreate infrastructure từ code trong 1 giờ, bạn đang sống nguy hiểm.*
