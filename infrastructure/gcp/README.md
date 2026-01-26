# GCP 인프라 코드 (Terraform)

이 디렉토리에는 GCP Vertex AI Agent를 위한 인프라를 정의하는 Terraform 코드가 포함됩니다.

## 구조

- `main.tf`: 메인 리소스 정의 (Cloud Storage, Cloud Functions 등)
- `variables.tf`: 변수 정의
- `outputs.tf`: 출력값 정의
- `terraform.tfvars.example`: 변수 값 예시

## 생성되는 리소스

- **Cloud Storage Bucket**: Knowledge Base 문서 저장
- **Cloud Functions**: 도구 구현용 (Lambda 대체)
- **Service Account**: Cloud Functions 실행용
- **Cloud Logging**: Agent 로깅
- **Cloud Monitoring**: 모니터링 (Production 환경)

## 사용 방법

### 1. GCP 인증 설정

```bash
# GCP CLI 로그인
gcloud auth login
gcloud auth application-default login

# 프로젝트 설정
gcloud config set project YOUR_PROJECT_ID
```

### 2. Terraform 초기화

```bash
cd infrastructure/gcp
terraform init
```

### 3. 변수 파일 생성

```bash
cp terraform.tfvars.example terraform.tfvars
# terraform.tfvars 파일을 편집하여 실제 값 입력
```

### 4. 계획 확인

```bash
terraform plan -var="environment=dev"
```

### 5. 인프라 배포

```bash
terraform apply -var="environment=dev"
```

### 6. 인프라 삭제

```bash
terraform destroy -var="environment=dev"
```

## 환경별 배포

### Dev 환경

```bash
terraform apply \
  -var="project_id=your-project-id" \
  -var="environment=dev"
```

### Staging 환경

```bash
terraform apply \
  -var="project_id=your-project-id" \
  -var="environment=staging"
```

### Production 환경

```bash
terraform apply \
  -var="project_id=your-project-id" \
  -var="environment=production"
```

## Vertex AI Search 설정

**참고**: Vertex AI Search는 현재 Terraform Provider에서 직접 지원하지 않으므로, 별도로 설정해야 합니다:

```bash
# Vertex AI Search Application 생성 (gcloud CLI 사용)
gcloud alpha discovery-engine data-stores create \
  --data-store-id=knowledge-base \
  --display-name="Knowledge Base" \
  --location=asia-northeast3 \
  --solution-type=SOLUTION_TYPE_SEARCH
```

또는 `infrastructure/scripts/deploy-gcp-infrastructure.sh` 스크립트를 사용하세요.

## 주의사항

1. **상태 파일 백엔드**: 프로덕션 환경에서는 GCS 백엔드를 사용하여 Terraform 상태를 저장하는 것을 권장합니다.

2. **비용**: Cloud Functions와 Cloud Storage는 사용량에 따라 비용이 발생합니다. Dev 환경에서는 적절한 리소스 제한을 설정하세요.

3. **보안**: `terraform.tfvars` 파일은 Git에 커밋하지 마세요. `.gitignore`에 포함되어 있습니다.

4. **권한**: 배포를 위해서는 적절한 GCP 권한이 필요합니다:
   - Storage Admin
   - Cloud Functions Admin
   - Service Account Admin
   - IAM Admin

5. **API 활성화**: 다음 API를 활성화해야 합니다:
   ```bash
   gcloud services enable \
     storage-api.googleapis.com \
     cloudfunctions.googleapis.com \
     cloudbuild.googleapis.com \
     aiplatform.googleapis.com
   ```
