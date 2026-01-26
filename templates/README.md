# Agent Templates

Agent 템플릿을 관리하는 디렉토리입니다. 새로운 Agent를 빠르게 생성하기 위한 템플릿을 제공합니다.

## 템플릿 목록

현재는 템플릿이 정의되지 않았습니다. 필요에 따라 다음 템플릿을 추가할 수 있습니다:

- `basic-agent-template/`: 기본 Agent 템플릿
  - 최소한의 Agent 정의
  - 기본 프롬프트 템플릿
  - 도구 없음

- `rag-agent-template/`: RAG Agent 템플릿
  - Knowledge Base 통합
  - 검색 도구 포함
  - 벡터 스토어 설정

- `multi-agent-template/`: Multi-Agent 템플릿
  - 여러 Agent 간 협업
  - Agent 간 통신 설정
  - 오케스트레이션 로직

## 템플릿 사용 방법

### 1. 템플릿에서 새 Agent 생성

```bash
# 템플릿 복사
cp -r templates/basic-agent-template agents/my-new-agent

# Agent 이름 변경
cd agents/my-new-agent
# agent-definition.yaml의 metadata.name 수정
```

### 2. 템플릿 구조

각 템플릿은 다음 구조를 가져야 합니다:

```
template-name/
├── agent-definition.yaml
├── prompts/
│   ├── system-prompt.md
│   └── user-prompt-template.md
├── tools/
│   ├── tool-definitions.yaml
│   └── implementations/
├── knowledge-base/
│   ├── data-sources.yaml
│   └── embedding-config.yaml
└── tests/
    ├── unit-tests.yaml
    ├── integration-tests.yaml
    └── evaluation-dataset.json
```

## 템플릿 추가 가이드

새 템플릿을 추가하려면:

1. `templates/` 디렉토리에 새 디렉토리 생성
2. 위의 템플릿 구조에 맞게 파일 생성
3. 예시 값으로 채우기
4. 이 README에 템플릿 설명 추가
