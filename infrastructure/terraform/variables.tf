# Terraform 변수 정의 파일

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

variable "opensearch_instance_type" {
  description = "OpenSearch 인스턴스 타입"
  type        = string
  default     = "t3.small.search"
}

variable "opensearch_instance_count" {
  description = "OpenSearch 인스턴스 개수"
  type        = number
  default     = 1
}

variable "opensearch_volume_size" {
  description = "OpenSearch EBS 볼륨 크기 (GB)"
  type        = number
  default     = 20
}
