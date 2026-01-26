#!/bin/bash
# 인프라 배포 스크립트
# Terraform을 사용하여 인프라를 배포합니다.

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

echo -e "${GREEN}Deploying infrastructure for environment: ${ENVIRONMENT}${NC}"

# Terraform 디렉토리로 이동
cd "$TERRAFORM_DIR"

# Terraform 초기화 (이미 초기화된 경우 스킵)
if [ ! -d ".terraform" ]; then
    echo -e "${YELLOW}Initializing Terraform...${NC}"
    terraform init
fi

# Terraform 계획
echo -e "${YELLOW}Running terraform plan...${NC}"
terraform plan \
    -var="environment=${ENVIRONMENT}" \
    -out=tfplan-${ENVIRONMENT}

# 사용자 확인
read -p "Do you want to apply these changes? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    echo -e "${YELLOW}Deployment cancelled${NC}"
    rm -f tfplan-${ENVIRONMENT}
    exit 0
fi

# Terraform 적용
echo -e "${YELLOW}Applying Terraform changes...${NC}"
terraform apply tfplan-${ENVIRONMENT}

# 출력값 표시
echo -e "${GREEN}Infrastructure deployed successfully!${NC}"
echo -e "${YELLOW}Outputs:${NC}"
terraform output

# 계획 파일 정리
rm -f tfplan-${ENVIRONMENT}

echo -e "${GREEN}Done!${NC}"
