# Agentic AI Ops Pipeline 프로젝트 구조

## 전체 프로젝트 구조

```
.
├── agents/                          # Agent 정의
│   └── customer-support-agent/
│       ├── agent-definition.yaml    # Agent 스키마 정의
│       ├── prompts/                 # 프롬프트 템플릿
│       │   ├── system-prompt.md
│       │   ├── user-prompt-template.md
│       │   └── versions/            # 프롬프트 버전 관리
│       │       ├── v1.0.0/
│       │       └── v1.2.0/
│       ├── tools/                   # 도구 정의 및 구현
│       │   ├── tool-definitions.yaml
│       │   └── implementations/    # 도구 구현 코드
│       │       ├── search-knowledge-base.py
│       │       ├── create-ticket.py
│       │       ├── requirements.txt
│       │       └── README.md
│       ├── knowledge-base/          # Knowledge Base 설정
│       │   ├── data-sources.yaml
│       │   └── embedding-config.yaml
│       └── tests/                   # 테스트 시나리오
│           ├── unit-tests.yaml
│           ├── integration-tests.yaml
│           └── evaluation-dataset.json
│
├── infrastructure/                  # 인프라 코드 (CSP별 분리)
│   ├── aws/                        # AWS Terraform 인프라
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── outputs.tf
│   │   ├── terraform.tfvars.example
│   │   └── README.md
│   ├── azure/                      # Azure Bicep 인프라
│   │   ├── main.bicep
│   │   ├── parameters.dev.bicepparam
│   │   ├── parameters.staging.bicepparam
│   │   ├── parameters.production.bicepparam
│   │   └── README.md
│   ├── gcp/                        # GCP Terraform 인프라
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── outputs.tf
│   │   ├── terraform.tfvars.example
│   │   └── README.md
│   ├── kubernetes/                 # Kubernetes 매니페스트
│   │   ├── namespace.yaml
│   │   ├── configmap.yaml
│   │   ├── secret.yaml.example
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   ├── ingress.yaml
│   │   └── README.md
│   ├── scripts/                    # 인프라 배포 스크립트
│   │   ├── deploy-infrastructure.sh        # AWS 배포
│   │   ├── destroy-infrastructure.sh       # AWS 삭제
│   │   ├── deploy-azure-infrastructure.sh  # Azure 배포
│   │   ├── destroy-azure-infrastructure.sh # Azure 삭제
│   │   ├── deploy-gcp-infrastructure.sh    # GCP 배포
│   │   ├── destroy-gcp-infrastructure.sh   # GCP 삭제
│   │   ├── deploy-kubernetes.sh            # Kubernetes 배포
│   │   └── README.md
│   └── README.md
│
├── pipelines/                      # CI/CD 파이프라인 정의 (템플릿)
│   ├── build-pipeline.yaml
│   ├── test-pipeline.yaml
│   ├── deploy-pipeline.yaml
│   └── evaluation-pipeline.yaml
│
├── .github/workflows/              # GitHub Actions 워크플로우
│   ├── build-pipeline.yml
│   ├── test-pipeline.yml
│   ├── deploy-pipeline.yml
│   └── evaluation-pipeline.yml
│
├── scripts/                        # 빌드/배포/검증 스크립트
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
│
├── tests/                          # 테스트 코드
│   ├── __init__.py
│   ├── unit/
│   │   ├── __init__.py
│   │   └── test_agent_definition.py
│   └── integration/
│       ├── __init__.py
│       └── test_agent_integration.py
│
├── templates/                      # Agent 템플릿
│   └── README.md
│
├── docs/                           # 문서
│   ├── README.md
│   └── GITHUB_SECRETS_SETUP.md
│
├── README.md                       # 프로젝트 메인 README
├── requirements.txt                # Python 의존성
├── Agentic_AI_Ops_Pipeline_Guide.md  # 전체 가이드 문서
└── PROJECT_STRUCTURE.md            # 이 파일
```

## 구조 검증 체크리스트

### ✅ 필수 디렉토리
- [x] `agents/` - Agent 정의
- [x] `infrastructure/` - 인프라 코드 (CSP별 분리)
  - [x] `aws/` - AWS Terraform
  - [x] `azure/` - Azure Bicep
  - [x] `gcp/` - GCP Terraform
  - [x] `kubernetes/` - Kubernetes 매니페스트
  - [x] `scripts/` - 배포 스크립트
- [x] `pipelines/` - 파이프라인 템플릿
- [x] `.github/workflows/` - GitHub Actions
- [x] `scripts/` - 빌드/배포 스크립트
- [x] `tests/` - 테스트 코드
- [x] `docs/` - 문서

### ✅ CSP별 지원
- [x] AWS: `infrastructure/aws/` (Terraform)
- [x] Azure: `infrastructure/azure/` (Bicep)
- [x] GCP: `infrastructure/gcp/` (Terraform)

### ✅ 필수 파일
- [x] Agent 정의: `agents/*/agent-definition.yaml`
- [x] 프롬프트: `agents/*/prompts/system-prompt.md`, `user-prompt-template.md`
- [x] 도구 정의: `agents/*/tools/tool-definitions.yaml`
- [x] 도구 구현: `agents/*/tools/implementations/`
- [x] Knowledge Base: `agents/*/knowledge-base/data-sources.yaml`, `embedding-config.yaml`
- [x] 테스트: `agents/*/tests/unit-tests.yaml`, `integration-tests.yaml`, `evaluation-dataset.json`

### ✅ CI/CD 파이프라인
- [x] Build Pipeline: `.github/workflows/build-pipeline.yml`
- [x] Test Pipeline: `.github/workflows/test-pipeline.yml`
- [x] Deploy Pipeline: `.github/workflows/deploy-pipeline.yml`
- [x] Evaluation Pipeline: `.github/workflows/evaluation-pipeline.yml`

### ✅ 스크립트
- [x] 검증 스크립트: `validate-*.py`, `check-security-policies.py`
- [x] 빌드 스크립트: `build-agent.py`
- [x] 배포 스크립트: `deploy-agent.py`
- [x] Knowledge Base: `sync-knowledge-base.py`
- [x] 평가 스크립트: `run-evaluation.py`, `generate-evaluation-report.py`
- [x] 모니터링: `monitor-deployment.py`, `smoke-tests.py`
- [x] 프롬프트 관리: `manage-prompt-versions.py`

### ✅ 문서
- [x] 메인 README: `README.md`
- [x] 가이드 문서: `Agentic_AI_Ops_Pipeline_Guide.md`
- [x] 문서 디렉토리: `docs/`
- [x] 각 하위 디렉토리 README

## 구조 일관성

### ✅ CSP별 일관된 구조
- 모든 CSP가 동일한 디렉토리 구조 사용
- `infrastructure/{csp}/` 형식으로 명확하게 구분
- 각 CSP별 배포/삭제 스크립트 제공

### ✅ 명명 규칙
- CSP 이름으로 폴더 구분: `aws/`, `azure/`, `gcp/`
- 스크립트 이름 일관성: `deploy-{csp}-infrastructure.sh`
- 환경별 파라미터 파일: `parameters.{env}.bicepparam` (Azure)

## 검증 완료

프로젝트 구조가 올바르게 구성되어 있으며, CSP별 지원이 일관되게 구현되어 있습니다.
