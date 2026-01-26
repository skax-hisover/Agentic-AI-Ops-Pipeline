# 프롬프트 버전 관리

이 디렉토리는 프롬프트의 버전별 히스토리를 관리합니다.

## 구조

```
versions/
├── v1.0.0/
│   ├── system-prompt.md
│   ├── user-prompt-template.md
│   └── metadata.yaml
├── v1.2.0/
│   ├── system-prompt.md
│   ├── user-prompt-template.md
│   └── metadata.yaml
└── README.md
```

## 버전 관리 방법

### 1. 새 버전 생성

프로젝트 루트의 `scripts/manage-prompt-versions.py` 스크립트를 사용:

```bash
# 프로젝트 루트에서 실행
python scripts/manage-prompt-versions.py \
  --agent-dir agents/customer-support-agent \
  --version v1.3.0 \
  --prompt-file prompts/system-prompt.md
```

### 2. 버전 태그

Git 태그로 `prompts/v1.0.0` 형식으로 관리:

```bash
git tag prompts/v1.0.0
git push origin prompts/v1.0.0
```

### 3. 메타데이터

각 버전 디렉토리의 `metadata.yaml`에 변경 이력 기록:
- 버전 번호
- 생성 일시
- Git 커밋 해시
- 변경 사항 설명

## 현재 사용 중인 버전

현재 `agent-definition.yaml`에서 참조하는 버전을 확인하세요:

```yaml
spec:
  prompts:
    version: v1.2.0  # 현재 사용 중인 버전
```

## 버전 롤백

이전 버전으로 롤백하려면:

1. `agent-definition.yaml`의 `spec.prompts.version` 필드를 변경
2. 빌드 파이프라인 재실행

## Semantic Versioning

프롬프트 버전은 Semantic Versioning을 따릅니다:
- **Major (v2.0.0)**: 프롬프트의 주요 변경 (Agent 동작에 큰 영향)
- **Minor (v1.2.0)**: 기능 추가 또는 개선
- **Patch (v1.0.1)**: 버그 수정 또는 작은 변경
