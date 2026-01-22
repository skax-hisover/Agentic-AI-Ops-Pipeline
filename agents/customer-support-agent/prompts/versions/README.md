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

1. **새 버전 생성**: `scripts/manage-prompt-versions.py` 스크립트 사용
2. **버전 태그**: Git 태그로 `prompts/v1.0.0` 형식으로 관리
3. **메타데이터**: 각 버전 디렉토리의 `metadata.yaml`에 변경 이력 기록

## 현재 사용 중인 버전

현재 `agent-definition.yaml`에서 참조하는 버전을 확인하세요:
- `spec.prompts.version` 필드
