# AI Agent CI/CD Pipeline

AI Agent 빌드 및 배포를 위한 전용 CI/CD 파이프라인입니다.

## 개요

이 프로젝트는 AI Agent의 빌드, 테스트, 배포를 자동화하는 CI/CD 파이프라인을 제공합니다. 프롬프트 버전 관리, Knowledge Base 동기화, 자동화된 평가 등을 지원합니다.

## 프로젝트 구조

```
.
├── agents/                    # Agent 정의
│   └── customer-support-agent/
│       ├── agent-definition.yaml
│       ├── prompts/
│       ├── tools/
│       ├── knowledge-base/
│       └── tests/
├── infrastructure/            # 인프라 코드
├── pipelines/                 # CI/CD 파이프라인 정의
├── scripts/                   # 빌드/배포 스크립트
├── tests/                     # 테스트 코드
└── .github/workflows/         # GitHub Actions 워크플로우
```

## 주요 기능

- **Agent 정의 검증**: 스키마 검증, 프롬프트 검증, 보안 정책 검증
- **자동화된 빌드**: CSP별 (AWS/Azure/GCP) Agent 아티팩트 생성
- **테스트 자동화**: 단위 테스트, 통합 테스트, 평가 테스트
- **Knowledge Base 동기화**: 벡터 인덱스 자동 업데이트
- **단계별 배포**: Dev → Staging → Production
- **평가 파이프라인**: 자동화된 평가 및 리포트 생성

## 시작하기

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. Agent 정의 검증

```bash
python scripts/validate-agent-definition.py agents/*/agent-definition.yaml
```

### 3. Agent 빌드

```bash
python scripts/build-agent.py --agent-dir agents/customer-support-agent
```

### 4. 평가 실행

```bash
python scripts/run-evaluation.py \
  --dataset agents/customer-support-agent/tests/evaluation-dataset.json \
  --agent agents/customer-support-agent
```

## CI/CD 파이프라인

### Build Pipeline
- Agent 정의 검증
- 프롬프트 검증
- 보안 정책 검증
- Agent 아티팩트 빌드

### Test Pipeline
- 단위 테스트
- 통합 테스트
- 평가 테스트

### Deploy Pipeline
- Dev 환경 배포
- Staging 환경 배포
- Production 환경 배포 (Canary 지원)

### Evaluation Pipeline
- 정기 평가 실행
- 베이스라인과 비교
- 리포트 생성

## 환경 변수 설정

GitHub Secrets에 다음 변수를 설정해야 합니다:

- `AWS_ACCESS_KEY_ID`: AWS 액세스 키
- `AWS_SECRET_ACCESS_KEY`: AWS 시크릿 키

## 참고 문서

- [Agentic AI Ops Pipeline Guide](./Agentic_AI_Ops_Pipeline_Guide.md)

## 라이선스

MIT
