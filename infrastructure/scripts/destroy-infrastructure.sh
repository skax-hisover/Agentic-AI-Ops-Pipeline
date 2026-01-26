#!/bin/bash
# 인프라 삭제 스크립트
# Terraform을 사용하여 인프라를 삭제합니다.

set -e  # 오류 발생 시 스크립트 중단

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 기본 변수
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="${SCRIPT_DIR}/../aws"
ENVIRONMENT="${1:-dev}"

# 환경 검증
if [[ ! "$ENVIRONMENT" =~ ^(dev|staging|production)$ ]]; then
    echo -e "${RED}Error: Environment must be dev, staging, or production${NC}"
    exit 1
fi

echo -e "${RED}WARNING: This will destroy all infrastructure for environment: ${ENVIRONMENT}${NC}"
echo -e "${YELLOW}This action cannot be undone!${NC}"

# 사용자 확인
read -p "Type 'yes' to confirm: " confirm
if [ "$confirm" != "yes" ]; then
    echo -e "${YELLOW}Destruction cancelled${NC}"
    exit 0
fi

# Terraform 디렉토리로 이동
cd "$TERRAFORM_DIR"

# Terraform 삭제
echo -e "${YELLOW}Destroying infrastructure...${NC}"
terraform destroy \
    -var="environment=${ENVIRONMENT}" \
    -auto-approve

echo -e "${GREEN}Infrastructure destroyed successfully!${NC}"
