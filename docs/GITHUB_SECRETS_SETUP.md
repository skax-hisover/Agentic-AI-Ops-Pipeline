# GitHub Secrets 설정 가이드

GitHub Actions에서 CSP별 자격증명을 사용하려면 GitHub Secrets에 다음 값들을 설정해야 합니다.

## 필수 Secrets 설정

### 1. GitHub 저장소에서 Secrets 설정

1. GitHub 저장소 페이지로 이동
2. **Settings** → **Secrets and variables** → **Actions** 클릭
3. **New repository secret** 버튼 클릭
4. 다음 Secrets를 추가:

#### AWS 자격증명 (AWS Agent 배포 시 필수)

- **Name**: `AWS_ACCESS_KEY_ID`
  - **Value**: AWS IAM 사용자의 Access Key ID

- **Name**: `AWS_SECRET_ACCESS_KEY`
  - **Value**: AWS IAM 사용자의 Secret Access Key

#### Azure 자격증명 (Azure Agent 배포 시 필수)

- **Name**: `AZURE_CREDENTIALS`
  - **Value**: Azure Service Principal의 JSON 형식 자격증명
  - 형식:
    ```json
    {
      "clientId": "your-client-id",
      "clientSecret": "your-client-secret",
      "subscriptionId": "your-subscription-id",
      "tenantId": "your-tenant-id"
    }
    ```

#### GCP 자격증명 (GCP Agent 배포 시 필수)

- **Name**: `GCP_SA_KEY`
  - **Value**: GCP Service Account의 JSON 키 파일 내용
  - 생성 방법:
    ```bash
    # GCP Service Account 생성 및 키 다운로드
    gcloud iam service-accounts create github-actions-deployer \
      --display-name="GitHub Actions Deployer"
    
    gcloud iam service-accounts keys create key.json \
      --iam-account=github-actions-deployer@PROJECT_ID.iam.gserviceaccount.com
    
    # key.json 파일의 전체 내용을 GCP_SA_KEY Secret에 복사
    ```

### 2. CSP별 자격증명 생성 및 권한 설정

#### AWS IAM 사용자 생성

```bash
# AWS CLI를 사용하여 IAM 사용자 생성
aws iam create-user --user-name github-actions-agent-deployer

# Access Key 생성
aws iam create-access-key --user-name github-actions-agent-deployer
```

#### Azure Service Principal 생성

```bash
# Azure CLI를 사용하여 Service Principal 생성
az login
az account set --subscription "your-subscription-id"

az ad sp create-for-rbac --name "github-actions-deployer" \
  --role contributor \
  --scopes /subscriptions/your-subscription-id \
  --sdk-auth

# 출력된 JSON을 AZURE_CREDENTIALS Secret에 복사
```

#### GCP Service Account 생성

```bash
# GCP Service Account 생성
gcloud iam service-accounts create github-actions-deployer \
  --display-name="GitHub Actions Deployer" \
  --project=YOUR_PROJECT_ID

# 필요한 권한 부여
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:github-actions-deployer@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/aiplatform.admin"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:github-actions-deployer@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/cloudfunctions.admin"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:github-actions-deployer@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.admin"

# 키 생성
gcloud iam service-accounts keys create key.json \
  --iam-account=github-actions-deployer@YOUR_PROJECT_ID.iam.gserviceaccount.com

# key.json 파일의 전체 내용을 GCP_SA_KEY Secret에 복사
```

#### AWS 필요한 IAM 권한

다음 정책을 IAM 사용자에게 연결해야 합니다:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:*",
        "lambda:*",
        "s3:GetObject",
        "s3:PutObject",
        "s3:ListBucket",
        "opensearch:*",
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents",
        "iam:PassRole"
      ],
      "Resource": "*"
    }
  ]
}
```

또는 더 제한적인 권한을 원하는 경우:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:CreateAgent",
        "bedrock:UpdateAgent",
        "bedrock:GetAgent",
        "bedrock:ListAgents",
        "bedrock:CreateAgentAlias",
        "bedrock:UpdateAgentAlias",
        "lambda:CreateFunction",
        "lambda:UpdateFunctionCode",
        "lambda:UpdateFunctionConfiguration",
        "lambda:InvokeFunction",
        "s3:GetObject",
        "s3:PutObject",
        "s3:ListBucket",
        "opensearch:ESHttpPost",
        "opensearch:ESHttpGet",
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": "iam:PassRole",
      "Resource": "arn:aws:iam::*:role/bedrock-agent-*"
    }
  ]
}
```

### 3. 환경별 Secrets (선택사항)

GitHub Environments를 사용하여 환경별로 다른 자격증명을 설정할 수 있습니다:

1. **Settings** → **Environments** 클릭
2. 환경 생성 (예: `development`, `staging`, `production`)
3. 각 환경에 환경별 Secrets 설정

## 테스트 파이프라인에서의 선택적 사용

`test-pipeline.yml`에서는 AWS 자격증명이 **선택사항**입니다:
- Secrets가 설정되어 있으면 실제 클라우드 리소스를 사용한 통합 테스트 실행
- Secrets가 없으면 로컬 테스트만 실행 (파이프라인은 계속 진행)

## 배포 파이프라인에서의 필수 사용

`deploy-pipeline.yml`에서는 사용하는 CSP에 따라 해당 자격증명이 **필수**입니다:
- Agent 정의에서 `provider: aws`인 경우: AWS 자격증명 필수
- Agent 정의에서 `provider: azure`인 경우: Azure 자격증명 필수
- Agent 정의에서 `provider: gcp`인 경우: GCP 자격증명 필수
- 파이프라인은 자동으로 Agent 정의를 확인하여 필요한 CSP 자격증명만 설정합니다

## 보안 모범 사례

1. **최소 권한 원칙**: 필요한 최소한의 권한만 부여
2. **정기적 로테이션**: Access Key를 정기적으로 교체
3. **환경 분리**: Dev/Staging/Production 환경별로 다른 자격증명 사용
4. **감사 로깅**: CloudTrail을 활성화하여 모든 API 호출 추적

## 문제 해결

### 오류: "Credentials could not be loaded"

**원인**: GitHub Secrets에 `AWS_ACCESS_KEY_ID` 또는 `AWS_SECRET_ACCESS_KEY`가 설정되지 않았거나 잘못 설정됨

**해결 방법**:
1. GitHub 저장소의 Settings → Secrets에서 값이 올바르게 설정되었는지 확인
2. Secret 이름이 정확한지 확인 (대소문자 구분)
3. Secret 값에 공백이나 특수문자가 포함되지 않았는지 확인

### 오류: "Access Denied"

**원인**: IAM 사용자에게 필요한 권한이 없음

**해결 방법**:
1. IAM 사용자에게 위의 권한 정책을 연결
2. CloudTrail 로그를 확인하여 어떤 권한이 필요한지 확인
