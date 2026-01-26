#!/bin/bash
# Azure 인프라 삭제 스크립트
# 리소스 그룹을 삭제하여 모든 Azure 리소스를 제거합니다.

set -e  # 오류 발생 시 스크립트 중단

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 기본 변수
ENVIRONMENT="${1:-dev}"
RESOURCE_GROUP="rg-agentic-ai-ops-${ENVIRONMENT}"

# 환경 검증
if [[ ! "$ENVIRONMENT" =~ ^(dev|staging|production)$ ]]; then
    echo -e "${RED}Error: Environment must be dev, staging, or production${NC}"
    exit 1
fi

# Production 환경 확인
if [ "$ENVIRONMENT" == "production" ]; then
    echo -e "${RED}WARNING: You are about to delete PRODUCTION infrastructure!${NC}"
    read -p "Type 'DELETE PRODUCTION' to confirm: " confirm
    if [ "$confirm" != "DELETE PRODUCTION" ]; then
        echo -e "${YELLOW}Deletion cancelled${NC}"
        exit 0
    fi
fi

# Azure CLI 설치 확인
if ! command -v az &> /dev/null; then
    echo -e "${RED}Error: Azure CLI is not installed.${NC}"
    exit 1
fi

# Azure 로그인 확인
if ! az account show &> /dev/null; then
    echo -e "${YELLOW}Azure CLI is not logged in. Please login...${NC}"
    az login
fi

echo -e "${RED}WARNING: This will delete all resources in resource group: ${RESOURCE_GROUP}${NC}"
read -p "Are you sure you want to continue? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    echo -e "${YELLOW}Deletion cancelled${NC}"
    exit 0
fi

# 리소스 그룹 삭제
echo -e "${YELLOW}Deleting resource group: ${RESOURCE_GROUP}${NC}"
az group delete \
    --name "$RESOURCE_GROUP" \
    --yes \
    --no-wait

echo -e "${GREEN}Resource group deletion initiated.${NC}"
echo -e "${YELLOW}Note: This may take several minutes to complete.${NC}"
