# 인프라 배포 스크립트

이 디렉토리에는 인프라 배포를 자동화하는 스크립트들이 포함됩니다.

## 스크립트 목록

### Terraform 관련

- `deploy-infrastructure.sh`: Terraform을 사용하여 인프라 배포
- `destroy-infrastructure.sh`: Terraform을 사용하여 인프라 삭제

### Kubernetes 관련

- `deploy-kubernetes.sh`: Kubernetes 매니페스트 적용

## 사용 방법

### Terraform 인프라 배포

```bash
# Dev 환경 배포
./deploy-infrastructure.sh dev

# Staging 환경 배포
./deploy-infrastructure.sh staging

# Production 환경 배포
./deploy-infrastructure.sh production
```

### Terraform 인프라 삭제

```bash
# 주의: 이 스크립트는 모든 인프라를 삭제합니다!
./destroy-infrastructure.sh dev
```

### Kubernetes 배포

```bash
# Dev 환경 배포
./deploy-kubernetes.sh dev

# Staging 환경 배포
./deploy-kubernetes.sh staging

# Production 환경 배포
./deploy-kubernetes.sh production
```

## 사전 요구사항

### Terraform 스크립트

- Terraform >= 1.0 설치
- AWS CLI 설정 및 자격증명
- 적절한 AWS 권한

### Kubernetes 스크립트

- kubectl 설치 및 설정
- Kubernetes 클러스터 접근 권한
- `secret.yaml` 파일 생성 (예시 파일에서 복사)

## 주의사항

1. **Production 환경**: Production 환경에 배포하기 전에 반드시 Dev/Staging에서 테스트하세요.

2. **Secret 관리**: `secret.yaml` 파일은 Git에 커밋하지 마세요.

3. **권한 확인**: 스크립트 실행 전에 필요한 권한이 있는지 확인하세요.

4. **백업**: 인프라 삭제 전에 중요한 데이터를 백업하세요.
