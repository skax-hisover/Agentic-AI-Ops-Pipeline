#!/bin/bash
# Azure 인프라 배포 스크립트
# Bicep을 사용하여 Azure 인프라를 배포합니다.

set -e  # 오류 발생 시 스크립트 중단

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 기본 변수
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BICEP_DIR="${SCRIPT_DIR}/../azure"
ENVIRONMENT="${1:-dev}"
RESOURCE_GROUP="rg-agentic-ai-ops-${ENVIRONMENT}"

# 환경 검증
if [[ ! "$ENVIRONMENT" =~ ^(dev|staging|production)$ ]]; then
    echo -e "${RED}Error: Environment must be dev, staging, or production${NC}"
    exit 1
fi

# Azure CLI 설치 확인
if ! command -v az &> /dev/null; then
    echo -e "${RED}Error: Azure CLI is not installed. Please install it first.${NC}"
    echo "Visit: https://docs.microsoft.com/cli/azure/install-azure-cli"
    exit 1
fi

# Azure 로그인 확인
if ! az account show &> /dev/null; then
    echo -e "${YELLOW}Azure CLI is not logged in. Please login...${NC}"
    az login
fi

echo -e "${GREEN}Deploying Azure infrastructure for environment: ${ENVIRONMENT}${NC}"

# 리소스 그룹 생성 (없는 경우)
if ! az group show --name "$RESOURCE_GROUP" &> /dev/null; then
    echo -e "${YELLOW}Creating resource group: ${RESOURCE_GROUP}${NC}"
    az group create \
        --name "$RESOURCE_GROUP" \
        --location koreacentral
else
    echo -e "${GREEN}Resource group already exists: ${RESOURCE_GROUP}${NC}"
fi

# Bicep 디렉토리로 이동
cd "$BICEP_DIR"

# Bicep 배포
echo -e "${YELLOW}Deploying Bicep template...${NC}"
az deployment group create \
    --resource-group "$RESOURCE_GROUP" \
    --template-file main.bicep \
    --parameters "@parameters.${ENVIRONMENT}.bicepparam" \
    --name "deployment-${ENVIRONMENT}-$(date +%Y%m%d-%H%M%S)"

# 출력값 표시
echo -e "${GREEN}Azure infrastructure deployed successfully!${NC}"
echo -e "${YELLOW}Outputs:${NC}"
az deployment group show \
    --resource-group "$RESOURCE_GROUP" \
    --name "deployment-${ENVIRONMENT}-$(date +%Y%m%d-%H%M%S)" \
    --query properties.outputs \
    --output table

echo -e "${GREEN}Done!${NC}"
