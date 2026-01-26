# GCP Terraform 출력값 정의

output "storage_bucket_name" {
  description = "Knowledge Base Cloud Storage 버킷 이름"
  value       = google_storage_bucket.knowledge_base.name
  sensitive   = false
}

output "storage_bucket_url" {
  description = "Knowledge Base Cloud Storage 버킷 URL"
  value       = google_storage_bucket.knowledge_base.url
  sensitive   = false
}

output "functions_service_account_email" {
  description = "Cloud Functions Service Account 이메일"
  value       = google_service_account.functions.email
  sensitive   = false
}

output "functions_name" {
  description = "Cloud Functions 이름"
  value       = google_cloudfunctions2_function.agent_tools.name
  sensitive   = false
}

output "functions_url" {
  description = "Cloud Functions URL"
  value       = google_cloudfunctions2_function.agent_tools.service_config[0].uri
  sensitive   = false
}

output "project_id" {
  description = "GCP 프로젝트 ID"
  value       = var.project_id
  sensitive   = false
}

output "region" {
  description = "GCP 리전"
  value       = var.region
  sensitive   = false
}
