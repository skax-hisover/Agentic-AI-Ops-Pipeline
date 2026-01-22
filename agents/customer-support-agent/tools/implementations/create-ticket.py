#!/usr/bin/env python3
"""
고객 지원 티켓 생성 도구 구현

이 함수는 Agent가 호출할 수 있는 도구의 실제 구현입니다.
외부 API를 호출하여 티켓을 생성합니다.
"""
import os
import json
import requests
from typing import Dict, Any, Optional
from datetime import datetime


def create_ticket(
    title: str,
    description: str,
    priority: str = "medium",
    customer_id: str = None
) -> Dict[str, Any]:
    """
    고객 지원 티켓을 생성합니다.
    
    Args:
        title: 티켓 제목
        description: 티켓 설명
        priority: 우선순위 (low, medium, high, urgent)
        customer_id: 고객 ID
    
    Returns:
        생성된 티켓 정보:
        {
            "ticket_id": "TICKET-12345",
            "status": "open",
            "created_at": "2024-01-01T00:00:00Z"
        }
    """
    # 실제 구현은 외부 티켓 시스템 API 호출
    # 예시: REST API 호출
    # api_endpoint = os.getenv('TICKET_API_ENDPOINT', 'https://api.example.com/tickets')
    # api_key = os.getenv('TICKET_API_KEY')
    # 
    # headers = {
    #     'Authorization': f'Bearer {api_key}',
    #     'Content-Type': 'application/json'
    # }
    # 
    # payload = {
    #     'title': title,
    #     'description': description,
    #     'priority': priority,
    #     'customer_id': customer_id
    # }
    # 
    # response = requests.post(
    #     api_endpoint,
    #     headers=headers,
    #     json=payload,
    #     timeout=10
    # )
    # 
    # if response.status_code == 201:
    #     ticket_data = response.json()
    #     return {
    #         "ticket_id": ticket_data['id'],
    #         "status": ticket_data['status'],
    #         "created_at": ticket_data['created_at']
    #     }
    # else:
    #     raise Exception(f"Failed to create ticket: {response.status_code}")
    
    # 임시 더미 구현 (실제 배포 시 위의 실제 구현으로 교체)
    print(f"Creating ticket: {title}")
    print(f"Priority: {priority}, Customer ID: {customer_id}")
    
    # 더미 티켓 생성 결과 반환
    ticket_id = f"TICKET-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    return {
        "ticket_id": ticket_id,
        "status": "open",
        "created_at": datetime.now().isoformat()
    }


# Lambda 함수 핸들러 (AWS Bedrock Agent용)
def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda 함수 핸들러
    
    Args:
        event: Lambda 이벤트 (Bedrock Agent에서 전달되는 파라미터 포함)
        context: Lambda 컨텍스트
    
    Returns:
        생성된 티켓 정보를 Bedrock Agent 형식으로 반환
    """
    # Bedrock Agent에서 전달되는 파라미터 추출
    parameters = event.get('parameters', {})
    title = parameters.get('title', '')
    description = parameters.get('description', '')
    priority = parameters.get('priority', 'medium')
    customer_id = parameters.get('customer_id', '')
    
    # 티켓 생성 실행
    result = create_ticket(title, description, priority, customer_id)
    
    # Bedrock Agent 형식으로 반환
    return {
        'statusCode': 200,
        'body': json.dumps(result)
    }


if __name__ == "__main__":
    # 로컬 테스트
    test_result = create_ticket(
        title="테스트 티켓",
        description="테스트용 티켓입니다",
        priority="medium",
        customer_id="test_customer_001"
    )
    print(json.dumps(test_result, indent=2, ensure_ascii=False))
