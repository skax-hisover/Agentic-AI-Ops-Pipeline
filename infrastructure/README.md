# Infrastructure

인프라 코드를 관리하는 디렉토리입니다.

## 구조

```
infrastructure/
├── aws/                # AWS Terraform 코드
│   ├── main.tf         # 메인 리소스 정의
│   ├── variables.tf    # 변수 정의
│   ├── outputs.tf      # 출력값 정의
│   ├── terraform.tfvars.example  # 변수 값 예시
│   └── README.md       # AWS Terraform 사용 가이드
├── azure/              # Azure Bicep 코드
│   ├── main.bicep      # 메인 Bicep 템플릿
│   ├── parameters.dev.bicepparam      # Dev 환경 파라미터
│   ├── parameters.staging.bicepparam  # Staging 환경 파라미터
│   ├── parameters.production.bicepparam # Production 환경 파라미터
│   └── README.md       # Azure Bicep 사용 가이드
├── gcp/                # GCP Terraform 코드
│   ├── main.tf         # 메인 리소스 정의
│   ├── variables.tf    # 변수 정의
│   ├── outputs.tf      # 출력값 정의
│   ├── terraform.tfvars.example  # 변수 값 예시
│   └── README.md       # GCP Terraform 사용 가이드
├── kubernetes/         # Kubernetes 매니페스트
│   ├── namespace.yaml  # 네임스페이스 정의
│   ├── configmap.yaml  # 설정 및 환경 변수
│   ├── secret.yaml.example  # 시크릿 예시
│   ├── deployment.yaml # Agent 서비스 배포
│   ├── service.yaml    # 서비스 엔드포인트
│   ├── ingress.yaml    # 외부 접근을 위한 Ingress
│   └── README.md       # Kubernetes 사용 가이드
└── scripts/            # 배포 스크립트
    ├── deploy-infrastructure.sh        # AWS Terraform 인프라 배포
    ├── destroy-infrastructure.sh        # AWS Terraform 인프라 삭제
    ├── deploy-azure-infrastructure.sh   # Azure Bicep 인프라 배포
    ├── destroy-azure-infrastructure.sh  # Azure 인프라 삭제
    ├── deploy-gcp-infrastructure.sh     # GCP Terraform 인프라 배포
    ├── destroy-gcp-infrastructure.sh   # GCP Terraform 인프라 삭제
    ├── deploy-kubernetes.sh             # Kubernetes 배포
    └── README.md       # 스크립트 사용 가이드
```

## 주요 기능

### AWS (Terraform)
- AWS Bedrock Agent를 위한 인프라 정의
- S3 버킷 (Knowledge Base 문서 저장)
- OpenSearch 도메인 (벡터 스토어)
- IAM 역할 (Lambda 및 Bedrock Agent용)
- CloudWatch Log Group

### Azure (Bicep)
- Azure OpenAI Assistant를 위한 인프라 정의
- Azure Storage Account (Knowledge Base 문서 저장)
- Azure Cognitive Search (벡터 스토어)
- Azure Functions (도구 구현용)
- Application Insights (모니터링)

### GCP (Terraform)
- GCP Vertex AI Agent를 위한 인프라 정의
- Cloud Storage Bucket (Knowledge Base 문서 저장)
- Cloud Functions (도구 구현용)
- Service Account 및 IAM 역할
- Cloud Logging 및 Monitoring

### Kubernetes
- Agent 서비스 배포 매니페스트
- ConfigMap 및 Secret 관리
- Service 및 Ingress 설정

### Scripts
- CSP별 인프라 배포 자동화 스크립트
- 환경별 배포 지원 (dev, staging, production)

## 빠른 시작

### AWS 인프라 배포

```bash
cd infrastructure/aws
cp terraform.tfvars.example terraform.tfvars
# terraform.tfvars 파일 편집
terraform init
terraform plan -var="environment=dev"
terraform apply -var="environment=dev"
```

또는 스크립트 사용:

```bash
./scripts/deploy-infrastructure.sh dev
```

### Azure 인프라 배포

```bash
# Azure CLI 로그인
az login

# 스크립트 사용 (권장)
./scripts/deploy-azure-infrastructure.sh dev
```

### GCP 인프라 배포

```bash
# GCP 인증
gcloud auth login
gcloud auth application-default login

# 스크립트 사용 (권장)
./scripts/deploy-gcp-infrastructure.sh dev YOUR_PROJECT_ID
```

### Kubernetes 배포

```bash
cd infrastructure/kubernetes
cp secret.yaml.example secret.yaml
# secret.yaml 파일 편집 (base64 인코딩된 값 입력)
kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
kubectl apply -f secret.yaml
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
```

또는 스크립트 사용:

```bash
./scripts/deploy-kubernetes.sh dev
```

## 환경별 배포

모든 스크립트와 Terraform 명령은 환경 변수를 지원합니다:

- `dev`: 개발 환경
- `staging`: 스테이징 환경
- `production`: 운영 환경

## 주의사항

1. **Secret 파일**: `terraform.tfvars`와 `kubernetes/secret.yaml`은 Git에 커밋하지 마세요.
2. **비용**: OpenSearch 도메인은 비용이 발생할 수 있습니다. Dev 환경에서는 작은 인스턴스를 사용하세요.
3. **권한**: 인프라 배포를 위해서는 적절한 AWS/Kubernetes 권한이 필요합니다.

자세한 내용은 각 하위 디렉토리의 README.md를 참고하세요.
