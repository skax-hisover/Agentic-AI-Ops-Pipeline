#!/bin/bash
# Kubernetes 배포 스크립트
# Kubernetes 매니페스트를 적용합니다.

set -e  # 오류 발생 시 스크립트 중단

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 기본 변수
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KUBERNETES_DIR="${SCRIPT_DIR}/../kubernetes"
ENVIRONMENT="${1:-dev}"

# 환경 검증
if [[ ! "$ENVIRONMENT" =~ ^(dev|staging|production)$ ]]; then
    echo -e "${RED}Error: Environment must be dev, staging, or production${NC}"
    exit 1
fi

echo -e "${GREEN}Deploying to Kubernetes for environment: ${ENVIRONMENT}${NC}"

# Kubernetes 컨텍스트 확인
if ! kubectl cluster-info &> /dev/null; then
    echo -e "${RED}Error: Kubernetes cluster is not accessible${NC}"
    exit 1
fi

# Kubernetes 디렉토리로 이동
cd "$KUBERNETES_DIR"

# 순서대로 리소스 배포
echo -e "${YELLOW}Creating namespace...${NC}"
kubectl apply -f namespace.yaml

echo -e "${YELLOW}Creating ConfigMap...${NC}"
kubectl apply -f configmap.yaml

# Secret 파일 확인
if [ ! -f "secret.yaml" ]; then
    echo -e "${RED}Error: secret.yaml not found. Please create it from secret.yaml.example${NC}"
    exit 1
fi

echo -e "${YELLOW}Creating Secret...${NC}"
kubectl apply -f secret.yaml

echo -e "${YELLOW}Creating Deployment...${NC}"
kubectl apply -f deployment.yaml

echo -e "${YELLOW}Creating Service...${NC}"
kubectl apply -f service.yaml

# Ingress는 선택사항
if [ -f "ingress.yaml" ]; then
    echo -e "${YELLOW}Creating Ingress...${NC}"
    kubectl apply -f ingress.yaml
fi

# 배포 상태 확인
echo -e "${YELLOW}Waiting for deployment to be ready...${NC}"
kubectl wait --for=condition=available --timeout=300s deployment/agent-service -n agentic-ai-ops || true

# 배포 정보 표시
echo -e "${GREEN}Deployment completed!${NC}"
echo -e "${YELLOW}Pod status:${NC}"
kubectl get pods -n agentic-ai-ops

echo -e "${YELLOW}Service status:${NC}"
kubectl get services -n agentic-ai-ops
