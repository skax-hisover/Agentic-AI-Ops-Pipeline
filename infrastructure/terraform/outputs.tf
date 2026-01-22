# Terraform 출력값 정의

output "s3_bucket_name" {
  description = "Knowledge Base S3 버킷 이름"
  value       = aws_s3_bucket.knowledge_base.id
}

output "opensearch_endpoint" {
  description = "OpenSearch 도메인 엔드포인트"
  value       = aws_opensearch_domain.vector_store.endpoint
  sensitive   = false
}

output "opensearch_domain_arn" {
  description = "OpenSearch 도메인 ARN"
  value       = aws_opensearch_domain.vector_store.arn
}

output "lambda_execution_role_arn" {
  description = "Lambda 실행 역할 ARN"
  value       = aws_iam_role.lambda_execution.arn
}

output "bedrock_agent_role_arn" {
  description = "Bedrock Agent 역할 ARN"
  value       = aws_iam_role.bedrock_agent.arn
}

output "cloudwatch_log_group_name" {
  description = "CloudWatch Log Group 이름"
  value       = aws_cloudwatch_log_group.agent_logs.name
}
