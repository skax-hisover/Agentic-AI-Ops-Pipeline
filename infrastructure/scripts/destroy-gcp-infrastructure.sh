#!/bin/bash
# GCP 인프라 삭제 스크립트
# Terraform을 사용하여 GCP 인프라를 삭제합니다.

set -e  # 오류 발생 시 스크립트 중단

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 기본 변수
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="${SCRIPT_DIR}/../gcp"
ENVIRONMENT="${1:-dev}"
PROJECT_ID="${2:-}"

# 환경 검증
if [[ ! "$ENVIRONMENT" =~ ^(dev|staging|production)$ ]]; then
    echo -e "${RED}Error: Environment must be dev, staging, or production${NC}"
    exit 1
fi

# 프로젝트 ID 확인
if [ -z "$PROJECT_ID" ]; then
    PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
    
    if [ -z "$PROJECT_ID" ]; then
        echo -e "${RED}Error: GCP Project ID is required.${NC}"
        echo "Usage: $0 <environment> <project-id>"
        exit 1
    fi
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

echo -e "${RED}WARNING: This will delete all GCP infrastructure for environment: ${ENVIRONMENT}${NC}"
echo -e "${RED}Project ID: ${PROJECT_ID}${NC}"
read -p "Are you sure you want to continue? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    echo -e "${YELLOW}Deletion cancelled${NC}"
    exit 0
fi

# Terraform 디렉토리로 이동
cd "$TERRAFORM_DIR"

# Terraform 초기화 (이미 초기화된 경우 스킵)
if [ ! -d ".terraform" ]; then
    echo -e "${YELLOW}Initializing Terraform...${NC}"
    terraform init
fi

# Terraform 삭제
echo -e "${YELLOW}Destroying GCP infrastructure...${NC}"
terraform destroy \
    -var="project_id=${PROJECT_ID}" \
    -var="environment=${ENVIRONMENT}" \
    -auto-approve

echo -e "${GREEN}GCP infrastructure destroyed successfully!${NC}"
