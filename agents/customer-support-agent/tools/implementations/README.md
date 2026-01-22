# 도구 구현 코드

이 디렉토리에는 Agent가 사용할 수 있는 도구들의 실제 구현 코드가 포함됩니다.

## 구조

```
implementations/
├── search-knowledge-base.py  # Knowledge Base 검색 도구 구현
├── create-ticket.py          # 티켓 생성 도구 구현
└── README.md                 # 이 파일
```

## 도구 타입별 배포 방식

### Function 타입 도구
- **AWS**: Lambda 함수로 배포
- **Azure**: Azure Functions로 배포
- **GCP**: Cloud Functions로 배포

### API 타입 도구
- 외부 API 엔드포인트를 직접 호출
- 인증 정보는 환경 변수나 시크릿 관리자에서 관리

## 구현 가이드

### 1. 로컬 테스트
각 구현 파일은 독립적으로 실행 가능합니다:

```bash
python search-knowledge-base.py
python create-ticket.py
```

### 2. Lambda 함수 배포 (AWS)
```bash
# Lambda 함수 패키징
zip -r search-knowledge-base.zip search-knowledge-base.py

# Lambda 함수 생성/업데이트
aws lambda create-function \
  --function-name search-knowledge-base \
  --runtime python3.11 \
  --handler search-knowledge-base.lambda_handler \
  --zip-file fileb://search-knowledge-base.zip
```

### 3. 환경 변수 설정
각 도구 구현은 다음 환경 변수를 사용할 수 있습니다:

- `OPENSEARCH_ENDPOINT`: OpenSearch 엔드포인트
- `OPENSEARCH_USER`: OpenSearch 사용자명
- `OPENSEARCH_PASSWORD`: OpenSearch 비밀번호
- `TICKET_API_ENDPOINT`: 티켓 API 엔드포인트
- `TICKET_API_KEY`: 티켓 API 키

## 주의사항

1. **더미 구현**: 현재 구현은 더미 데이터를 반환합니다. 실제 배포 시 실제 API/서비스 연동 코드로 교체해야 합니다.

2. **에러 처리**: 실제 구현에서는 네트워크 오류, 타임아웃 등을 적절히 처리해야 합니다.

3. **로깅**: 운영 환경에서는 적절한 로깅을 추가하여 디버깅과 모니터링을 지원해야 합니다.

4. **보안**: API 키, 비밀번호 등은 절대 코드에 하드코딩하지 말고 환경 변수나 시크릿 관리자를 사용하세요.
