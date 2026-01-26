# GCP Vertex AI Agent 인프라를 위한 Terraform 설정
# Cloud Storage, Vertex AI Search, Cloud Functions 등을 생성

terraform {
  required_version = ">= 1.0"
  
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
  
  # Terraform 상태 파일 저장 위치 (GCS 백엔드 사용 권장)
  # backend "gcs" {
  #   bucket = "your-terraform-state-bucket"
  #   prefix = "agentic-ai-ops/terraform.tfstate"
  # }
}

provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

# 변수 정의
variable "project_id" {
  description = "GCP 프로젝트 ID"
  type        = string
}

variable "region" {
  description = "GCP 리전"
  type        = string
  default     = "asia-northeast3"  # 서울
}

variable "zone" {
  description = "GCP 존"
  type        = string
  default     = "asia-northeast3-a"
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

# Cloud Storage Bucket (Knowledge Base 문서 저장용)
resource "google_storage_bucket" "knowledge_base" {
  name          = "${var.agent_name}-kb-${var.environment}-${random_id.bucket_suffix.hex}"
  location      = var.region
  force_destroy = var.environment != "production"
  
  uniform_bucket_level_access {
    enabled = true
  }
  
  versioning {
    enabled = true
  }
  
  lifecycle_rule {
    condition {
      age = var.environment == "production" ? 90 : 30
    }
    action {
      type = "Delete"
    }
  }
  
  labels = {
    project     = "agentic-ai-ops"
    environment = var.environment
    managed-by  = "terraform"
  }
}

# Random ID for bucket name uniqueness
resource "random_id" "bucket_suffix" {
  byte_length = 4
}

# Cloud Storage Bucket IAM (Functions 액세스용)
resource "google_storage_bucket_iam_member" "functions_access" {
  bucket = google_storage_bucket.knowledge_base.name
  role   = "roles/storage.objectViewer"
  member = "serviceAccount:${google_service_account.functions.email}"
}

# Vertex AI Search Application (벡터 스토어용)
# Note: Vertex AI Search는 현재 Terraform Provider에서 직접 지원하지 않으므로
# gcloud CLI를 사용하거나 별도 스크립트로 생성해야 합니다.
# 여기서는 기본 구조만 정의합니다.

# Cloud Functions Service Account
resource "google_service_account" "functions" {
  account_id   = "${var.agent_name}-functions-${var.environment}"
  display_name = "Cloud Functions Service Account for ${var.agent_name}"
  
  labels = {
    project     = "agentic-ai-ops"
    environment = var.environment
    managed-by  = "terraform"
  }
}

# Cloud Functions Service Account IAM 역할
resource "google_project_iam_member" "functions_vertex_ai" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.functions.email}"
}

resource "google_project_iam_member" "functions_storage" {
  project = var.project_id
  role    = "roles/storage.objectViewer"
  member  = "serviceAccount:${google_service_account.functions.email}"
}

# Cloud Functions (도구 구현용)
# Note: 실제 함수 코드는 별도로 배포해야 합니다.
resource "google_cloudfunctions2_function" "agent_tools" {
  name        = "${var.agent_name}-tools-${var.environment}"
  location    = var.region
  description = "Agent tools implementation for ${var.agent_name}"
  
  build_config {
    runtime     = "python311"
    entry_point = "main"
    source {
      storage_source {
        bucket = google_storage_bucket.knowledge_base.name
        object = "functions/source.zip"
      }
    }
  }
  
  service_config {
    max_instance_count    = var.environment == "production" ? 100 : 10
    min_instance_count    = var.environment == "production" ? 1 : 0
    available_memory      = "256Mi"
    timeout_seconds      = 60
    service_account_email = google_service_account.functions.email
    
    environment_variables = {
      GCP_PROJECT_ID     = var.project_id
      GCP_REGION         = var.region
      STORAGE_BUCKET     = google_storage_bucket.knowledge_base.name
      ENVIRONMENT        = var.environment
    }
  }
  
  labels = {
    project     = "agentic-ai-ops"
    environment = var.environment
    managed-by  = "terraform"
  }
}

# Cloud Logging (Agent 로깅용)
resource "google_logging_project_sink" "agent_logs" {
  name        = "${var.agent_name}-logs-${var.environment}"
  destination = "logging.googleapis.com/projects/${var.project_id}"
  
  filter = "resource.type=\"cloud_function\" AND resource.labels.function_name=\"${google_cloudfunctions2_function.agent_tools.name}\""
  
  unique_writer_identity = true
}

# Cloud Monitoring Alert Policy (선택사항)
resource "google_monitoring_alert_policy" "function_errors" {
  count        = var.environment == "production" ? 1 : 0
  display_name = "${var.agent_name} Function Errors"
  combiner     = "OR"
  
  conditions {
    display_name = "Function error rate"
    condition_threshold {
      filter          = "resource.type=\"cloud_function\" AND resource.labels.function_name=\"${google_cloudfunctions2_function.agent_tools.name}\""
      duration        = "300s"
      comparison      = "COMPARISON_GT"
      threshold_value = 0.1
    }
  }
  
  notification_channels = []  # 필요 시 추가
}

# 출력값
output "storage_bucket_name" {
  description = "Knowledge Base Cloud Storage 버킷 이름"
  value       = google_storage_bucket.knowledge_base.name
}

output "storage_bucket_url" {
  description = "Knowledge Base Cloud Storage 버킷 URL"
  value       = google_storage_bucket.knowledge_base.url
}

output "functions_service_account_email" {
  description = "Cloud Functions Service Account 이메일"
  value       = google_service_account.functions.email
}

output "functions_name" {
  description = "Cloud Functions 이름"
  value       = google_cloudfunctions2_function.agent_tools.name
}

output "functions_url" {
  description = "Cloud Functions URL"
  value       = google_cloudfunctions2_function.agent_tools.service_config[0].uri
}

output "project_id" {
  description = "GCP 프로젝트 ID"
  value       = var.project_id
}

output "region" {
  description = "GCP 리전"
  value       = var.region
}
