# Terraform 인프라 코드

이 디렉토리에는 AWS Bedrock Agent를 위한 인프라를 정의하는 Terraform 코드가 포함됩니다.

## 구조

- `main.tf`: 메인 리소스 정의 (S3, OpenSearch, IAM 역할 등)
- `variables.tf`: 변수 정의
- `outputs.tf`: 출력값 정의
- `terraform.tfvars.example`: 변수 값 예시

## 사용 방법

### 1. 변수 파일 생성

```bash
cp terraform.tfvars.example terraform.tfvars
# terraform.tfvars 파일을 편집하여 실제 값 입력
```

### 2. Terraform 초기화

```bash
terraform init
```

### 3. 계획 확인

```bash
terraform plan -var="environment=dev"
```

### 4. 인프라 배포

```bash
terraform apply -var="environment=dev"
```

### 5. 인프라 삭제

```bash
terraform destroy -var="environment=dev"
```

## 환경별 배포

### Dev 환경

```bash
terraform apply -var="environment=dev"
```

### Staging 환경

```bash
terraform apply -var="environment=staging"
```

### Production 환경

```bash
terraform apply -var="environment=production"
```

## 생성되는 리소스

- **S3 버킷**: Knowledge Base 문서 저장
- **OpenSearch 도메인**: 벡터 스토어
- **IAM 역할**: Lambda 실행 및 Bedrock Agent용
- **CloudWatch Log Group**: Agent 로깅

## 주의사항

1. **상태 파일 백엔드**: 프로덕션 환경에서는 S3 백엔드를 사용하여 Terraform 상태를 저장하는 것을 권장합니다.

2. **비용**: OpenSearch 도메인은 비용이 발생할 수 있습니다. Dev 환경에서는 작은 인스턴스 타입을 사용하세요.

3. **보안**: `terraform.tfvars` 파일은 Git에 커밋하지 마세요. `.gitignore`에 포함되어 있습니다.
