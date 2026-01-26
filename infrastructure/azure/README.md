# Azure 인프라 코드 (Bicep)

이 디렉토리에는 Azure OpenAI Assistant를 위한 인프라를 정의하는 Bicep 템플릿이 포함됩니다.

## 구조

- `main.bicep`: 메인 리소스 정의 (Storage Account, Azure Cognitive Search, Azure Functions 등)
- `parameters.dev.bicepparam`: Dev 환경 파라미터
- `parameters.staging.bicepparam`: Staging 환경 파라미터
- `parameters.production.bicepparam`: Production 환경 파라미터

## 생성되는 리소스

- **Azure Storage Account**: Knowledge Base 문서 저장
- **Azure Blob Container**: Knowledge Base 문서용 컨테이너
- **Azure Cognitive Search**: 벡터 스토어 (Azure Search)
- **Azure Functions**: 도구 구현용 (Lambda 대체)
- **Application Insights**: 모니터링 및 로깅

## 사용 방법

### 1. Azure CLI 로그인

```bash
az login
az account set --subscription "your-subscription-id"
```

### 2. 리소스 그룹 생성

```bash
# Dev 환경
az group create --name rg-agentic-ai-ops-dev --location koreacentral

# Staging 환경
az group create --name rg-agentic-ai-ops-staging --location koreacentral

# Production 환경
az group create --name rg-agentic-ai-ops-prod --location koreacentral
```

### 3. Bicep 배포

```bash
# Dev 환경 배포
az deployment group create \
  --resource-group rg-agentic-ai-ops-dev \
  --template-file main.bicep \
  --parameters @parameters.dev.bicepparam

# Staging 환경 배포
az deployment group create \
  --resource-group rg-agentic-ai-ops-staging \
  --template-file main.bicep \
  --parameters @parameters.staging.bicepparam

# Production 환경 배포
az deployment group create \
  --resource-group rg-agentic-ai-ops-prod \
  --template-file main.bicep \
  --parameters @parameters.production.bicepparam
```

### 4. 배포 확인

```bash
az deployment group show \
  --resource-group rg-agentic-ai-ops-dev \
  --name main
```

### 5. 출력값 확인

```bash
az deployment group show \
  --resource-group rg-agentic-ai-ops-dev \
  --name main \
  --query properties.outputs
```

## 환경별 설정

### Dev 환경
- Azure Cognitive Search: Basic SKU
- Storage Account: Standard_LRS
- Functions: Consumption Plan

### Staging 환경
- Azure Cognitive Search: Standard SKU
- Storage Account: Standard_LRS
- Functions: Consumption Plan

### Production 환경
- Azure Cognitive Search: Standard2 SKU (2 replicas, 2 partitions)
- Storage Account: Standard_LRS
- Functions: Consumption Plan

## 주의사항

1. **비용**: Azure Cognitive Search는 비용이 발생할 수 있습니다. Dev 환경에서는 Basic SKU를 사용하세요.

2. **보안**: 파라미터 파일에 민감한 정보가 포함되어 있지 않지만, 실제 배포 시에는 Azure Key Vault를 사용하는 것을 권장합니다.

3. **리전**: 기본 리전은 `koreacentral`입니다. 필요에 따라 변경하세요.

4. **권한**: 배포를 위해서는 적절한 Azure 권한이 필요합니다 (Contributor 또는 Owner).
