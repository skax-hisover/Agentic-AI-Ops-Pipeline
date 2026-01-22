# Kubernetes 매니페스트

이 디렉토리에는 Agent 서비스를 Kubernetes에 배포하기 위한 매니페스트 파일들이 포함됩니다.

## 파일 구조

- `namespace.yaml`: 네임스페이스 정의
- `configmap.yaml`: 설정 및 환경 변수
- `secret.yaml.example`: 시크릿 예시 (실제 값으로 복사하여 사용)
- `deployment.yaml`: Agent 서비스 배포 정의
- `service.yaml`: 서비스 엔드포인트 정의
- `ingress.yaml`: 외부 접근을 위한 Ingress 정의

## 사용 방법

### 1. Secret 파일 생성

```bash
cp secret.yaml.example secret.yaml
# secret.yaml 파일을 편집하여 base64 인코딩된 값 입력
```

### 2. 네임스페이스 생성

```bash
kubectl apply -f namespace.yaml
```

### 3. ConfigMap 및 Secret 생성

```bash
kubectl apply -f configmap.yaml
kubectl apply -f secret.yaml
```

### 4. 배포

```bash
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f ingress.yaml  # 선택사항
```

### 5. 배포 확인

```bash
kubectl get pods -n agentic-ai-ops
kubectl get services -n agentic-ai-ops
kubectl get ingress -n agentic-ai-ops
```

### 6. 로그 확인

```bash
kubectl logs -f deployment/agent-service -n agentic-ai-ops
```

## 환경별 배포

### Dev 환경

```bash
# namespace.yaml의 environment 레이블을 dev로 설정
kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
kubectl apply -f secret.yaml
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
```

### Staging/Production 환경

환경별로 별도의 네임스페이스를 사용하거나, 레이블을 변경하여 배포할 수 있습니다.

## 주의사항

1. **Secret 관리**: 실제 운영 환경에서는 Kubernetes Secrets 대신 AWS Secrets Manager나 HashiCorp Vault 같은 외부 시크릿 관리자를 사용하는 것을 권장합니다.

2. **이미지**: `deployment.yaml`의 이미지 경로를 실제 컨테이너 레지스트리로 변경해야 합니다.

3. **리소스 제한**: 환경에 맞게 `deployment.yaml`의 리소스 요청/제한을 조정하세요.

4. **Ingress**: Ingress Controller가 설치되어 있어야 `ingress.yaml`을 사용할 수 있습니다.
