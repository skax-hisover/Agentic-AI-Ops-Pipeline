# AI Agent CI/CD Pipeline

AI Agent 빌드 및 배포를 위한 전용 CI/CD 파이프라인입니다.

## 개요

이 프로젝트는 AI Agent의 빌드, 테스트, 배포를 자동화하는 CI/CD 파이프라인을 제공합니다. 프롬프트 버전 관리, Knowledge Base 동기화, 자동화된 평가 등을 지원합니다.

## 프로젝트 구조

```
.
├── agents/                    # Agent 정의
│   └── customer-support-agent/
│       ├── agent-definition.yaml      # Agent 스키마 정의
│       ├── prompts/                    # 프롬프트 템플릿
│       │   ├── system-prompt.md
│       │   ├── user-prompt-template.md
│       │   └── versions/              # 프롬프트 버전 관리
│       ├── tools/                      # 도구 정의 및 구현
│       │   ├── tool-definitions.yaml
│       │   └── implementations/       # 도구 구현 코드
│       ├── knowledge-base/            # Knowledge Base 설정
│       │   ├── data-sources.yaml
│       │   └── embedding-config.yaml
│       └── tests/                      # 테스트 시나리오
│           ├── unit-tests.yaml
│           ├── integration-tests.yaml
│           └── evaluation-dataset.json
├── infrastructure/            # 인프라 코드
│   ├── aws/                   # AWS Terraform 인프라 정의
│   ├── azure/                 # Azure Bicep 인프라 정의
│   ├── gcp/                   # GCP Terraform 인프라 정의
│   ├── kubernetes/            # Kubernetes 매니페스트
│   └── scripts/               # 배포 스크립트
├── pipelines/                 # CI/CD 파이프라인 정의 (템플릿)
│   ├── build-pipeline.yaml
│   ├── test-pipeline.yaml
│   ├── deploy-pipeline.yaml
│   └── evaluation-pipeline.yaml
├── .github/workflows/         # GitHub Actions 워크플로우
│   ├── build-pipeline.yml
│   ├── test-pipeline.yml
│   ├── deploy-pipeline.yml
│   └── evaluation-pipeline.yml
├── scripts/                   # 빌드/배포/검증 스크립트
│   ├── validate-agent-definition.py
│   ├── validate-prompts.py
│   ├── validate-tools.py
│   ├── check-security-policies.py
│   ├── build-agent.py
│   ├── deploy-agent.py
│   ├── sync-knowledge-base.py
│   ├── run-evaluation.py
│   ├── monitor-deployment.py
│   ├── test-prompt-rendering.py
│   ├── generate-evaluation-report.py
│   ├── compare-evaluation-results.py
│   ├── smoke-tests.py
│   └── manage-prompt-versions.py
├── tests/                     # 테스트 코드
│   ├── unit/
│   └── integration/
├── templates/                 # Agent 템플릿
├── docs/                      # 문서
│   ├── README.md
│   └── GITHUB_SECRETS_SETUP.md
├── README.md                  # 프로젝트 메인 README
├── requirements.txt           # Python 의존성
└── Agentic_AI_Ops_Pipeline_Guide.md  # 전체 가이드 문서
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

```powershell
python scripts/run-evaluation.py --dataset agents/customer-support-agent/tests/evaluation-dataset.json --agent agents/customer-support-agent
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

- [Agentic AI Ops Pipeline Guide](./Agentic_AI_Ops_Pipeline_Guide.md): 전체 가이드 문서
- [GitHub Secrets 설정 가이드](./docs/GITHUB_SECRETS_SETUP.md): GitHub Actions에서 AWS 자격증명 설정 방법
- [Infrastructure README](./infrastructure/README.md): 인프라 코드 사용 가이드
- [AWS Terraform README](./infrastructure/aws/README.md): AWS Terraform 인프라 배포 가이드
- [Kubernetes README](./infrastructure/kubernetes/README.md): Kubernetes 배포 가이드

## 라이선스

MIT
