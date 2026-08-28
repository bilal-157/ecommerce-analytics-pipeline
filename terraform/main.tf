provider "aws" {
  region = "us-east-1"
}

resource "aws_s3_bucket" "data_lake" {
  bucket = "ecommerce-data-lake-${random_string.suffix.id}"
  force_destroy = true
  
  tags = {
    Project = "EcommerceAnalytics"
    Environment = "dev"
  }
}

resource "random_string" "suffix" {
  length = 8
  special = false
}

resource "aws_db_instance" "warehouse" {
  identifier = "ecommerce-dw"
  engine = "postgres"
  engine_version = "14"
  instance_class = "db.t3.micro"
  allocated_storage = 20
  db_name = "ecommercedw"
  username = "admin"
  password = "SecurePassword123"
  skip_final_snapshot = true
  
  tags = {
    Project = "EcommerceAnalytics"
  }
}

output "s3_bucket" {
  value = aws_s3_bucket.data_lake.bucket
}

output "rds_endpoint" {
  value = aws_db_instance.warehouse.endpoint
}
