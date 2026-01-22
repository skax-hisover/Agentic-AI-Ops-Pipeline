# Terraform 메인 설정 파일
# AWS Bedrock Agent 인프라를 위한 기본 설정

terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  
  # Terraform 상태 파일 저장 위치 (S3 백엔드 사용 권장)
  # backend "s3" {
  #   bucket = "your-terraform-state-bucket"
  #   key    = "agentic-ai-ops/terraform.tfstate"
  #   region = "us-east-1"
  # }
}

provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Project     = "Agentic-AI-Ops"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

# 변수 정의
variable "aws_region" {
  description = "AWS 리전"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "환경 (dev, staging, production)"
  type        = string
  validation {
    condition     = contains(["dev", "staging", "production"], var.environment)
    error_message = "Environment must be dev, staging, or production."
  }
}

variable "agent_name" {
  description = "Agent 이름"
  type        = string
  default     = "customer-support-agent"
}

# S3 버킷 (Knowledge Base 문서 저장용)
resource "aws_s3_bucket" "knowledge_base" {
  bucket = "${var.agent_name}-kb-${var.environment}-${data.aws_caller_identity.current.account_id}"
  
  tags = {
    Name        = "${var.agent_name}-knowledge-base-${var.environment}"
    Purpose     = "Knowledge Base documents"
  }
}

resource "aws_s3_bucket_versioning" "knowledge_base" {
  bucket = aws_s3_bucket.knowledge_base.id
  versioning_configuration {
    status = "Enabled"
  }
}

# OpenSearch 도메인 (벡터 스토어용)
resource "aws_opensearch_domain" "vector_store" {
  domain_name    = "${var.agent_name}-vector-store-${var.environment}"
  engine_version = "OpenSearch_2.3"
  
  cluster_config {
    instance_type  = var.environment == "production" ? "r6g.large.search" : "t3.small.search"
    instance_count = var.environment == "production" ? 2 : 1
  }
  
  ebs_options {
    ebs_enabled = true
    volume_size = var.environment == "production" ? 100 : 20
    volume_type = "gp3"
  }
  
  node_to_node_encryption {
    enabled = true
  }
  
  encrypt_at_rest {
    enabled = true
  }
  
  domain_endpoint_options {
    enforce_https       = true
    tls_security_policy = "Policy-Min-TLS-1-2-2019-07"
  }
  
  tags = {
    Name = "${var.agent_name}-vector-store-${var.environment}"
  }
}

# Lambda 함수용 IAM 역할 (도구 구현용)
resource "aws_iam_role" "lambda_execution" {
  name = "${var.agent_name}-lambda-role-${var.environment}"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
  
  tags = {
    Name = "${var.agent_name}-lambda-role-${var.environment}"
  }
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "lambda_opensearch" {
  name = "${var.agent_name}-lambda-opensearch-${var.environment}"
  role = aws_iam_role.lambda_execution.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "es:ESHttpGet",
          "es:ESHttpPost",
          "es:ESHttpPut"
        ]
        Resource = "${aws_opensearch_domain.vector_store.arn}/*"
      }
    ]
  })
}

resource "aws_iam_role_policy" "lambda_s3" {
  name = "${var.agent_name}-lambda-s3-${var.environment}"
  role = aws_iam_role.lambda_execution.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.knowledge_base.arn,
          "${aws_s3_bucket.knowledge_base.arn}/*"
        ]
      }
    ]
  })
}

# Bedrock Agent용 IAM 역할
resource "aws_iam_role" "bedrock_agent" {
  name = "${var.agent_name}-bedrock-agent-role-${var.environment}"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "bedrock.amazonaws.com"
        }
      }
    ]
  })
  
  tags = {
    Name = "${var.agent_name}-bedrock-agent-role-${var.environment}"
  }
}

resource "aws_iam_role_policy" "bedrock_agent_lambda" {
  name = "${var.agent_name}-bedrock-agent-lambda-${var.environment}"
  role = aws_iam_role.bedrock_agent.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "lambda:InvokeFunction"
        ]
        Resource = "arn:aws:lambda:${var.aws_region}:*:function:${var.agent_name}-*"
      }
    ]
  })
}

# CloudWatch Log Group (Agent 로깅용)
resource "aws_cloudwatch_log_group" "agent_logs" {
  name              = "/aws/bedrock/agents/${var.agent_name}-${var.environment}"
  retention_in_days = var.environment == "production" ? 30 : 7
  
  tags = {
    Name = "${var.agent_name}-logs-${var.environment}"
  }
}

# 출력값
output "s3_bucket_name" {
  description = "Knowledge Base S3 버킷 이름"
  value       = aws_s3_bucket.knowledge_base.id
}

output "opensearch_endpoint" {
  description = "OpenSearch 도메인 엔드포인트"
  value       = aws_opensearch_domain.vector_store.endpoint
}

output "lambda_execution_role_arn" {
  description = "Lambda 실행 역할 ARN"
  value       = aws_iam_role.lambda_execution.arn
}

output "bedrock_agent_role_arn" {
  description = "Bedrock Agent 역할 ARN"
  value       = aws_iam_role.bedrock_agent.arn
}

# 현재 AWS 계정 정보
data "aws_caller_identity" "current" {}
