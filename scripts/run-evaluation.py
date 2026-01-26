#!/usr/bin/env python3
"""
Agent 평가 실행 스크립트

- tests/evaluation-dataset.json 과 같은 평가 데이터셋을 읽고
- Agent를 호출(invoke_agent)하여 응답을 수집한 뒤
- accuracy / relevance / completeness / toolUsageCorrectness 등의 메트릭을 계산한다.

CI/CD Test/Evaluation Stage 및 정기 평가 파이프라인에서 공통으로 사용하는 핵심 로직.
"""
import json
import yaml
import os
import argparse
import sys
import time
from typing import Dict, Any, List
from datetime import datetime


def invoke_agent(agent_def: Dict[str, Any], input_text: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Agent 호출 (실제 구현은 CSP별 SDK 사용)

    - 현재는 더미 응답을 반환하지만,
    - provider(aws/azure/gcp)에 따라 Bedrock Runtime / Azure OpenAI / Vertex AI 등을 호출하도록
      구현을 교체하면 된다.
    """
    # 실제 구현은 CSP별 Agent API 호출
    # 예시:
    # if provider == "aws":
    #     import boto3
    #     bedrock = boto3.client('bedrock-runtime')
    #     response = bedrock.invoke_agent(...)
    # elif provider == "azure":
    #     from openai import AzureOpenAI  # openai 패키지에서 AzureOpenAI 클래스 제공
    #     client = AzureOpenAI(...)
    #     response = client.beta.threads.messages.create(...)
    
    # 임시 더미 응답
    return {
        "response": f"Agent response to: {input_text}",
        "tools_used": ["search-knowledge-base"],
        "timestamp": datetime.now().isoformat()
    }


def calculate_accuracy(response: str, expected: Dict[str, Any]) -> float:
    """
    정확도 계산 (간단한 키워드 기반)

    - expected.expectedResponse 에 포함된 단어들이
      실제 응답에 얼마나 많이 등장하는지를 비율로 계산한다.
    """
    expected_text = expected.get("expectedResponse", "").lower()
    response_lower = response.lower()
    
    # 키워드 매칭
    expected_keywords = set(expected_text.split())
    response_keywords = set(response_lower.split())
    
    if not expected_keywords:
        return 1.0
    
    matched = len(expected_keywords & response_keywords)
    accuracy = matched / len(expected_keywords)
    
    return min(accuracy, 1.0)


def calculate_relevance(response: str, expected: Dict[str, Any]) -> float:
    """
    관련성 계산 (intent 기반 간단 버전)

    - intent 값(return_request 등)에 따라 정의된 키워드 집합을
      응답 문자열에서 얼마나 발견하는지로 관련성을 추정한다.
    """
    intent = expected.get("intent", "")
    response_lower = response.lower()
    
    # Intent 키워드가 응답에 포함되어 있는지 확인
    intent_keywords = {
        "return_request": ["반품", "환불", "return"],
        "delivery_inquiry": ["배송", "delivery", "shipping"],
        "product_inquiry": ["제품", "product", "상품"]
    }
    
    if intent in intent_keywords:
        keywords = intent_keywords[intent]
        found = sum(1 for kw in keywords if kw in response_lower)
        relevance = found / len(keywords) if keywords else 0.0
    else:
        relevance = 0.5  # 기본값
    
    return relevance


def calculate_completeness(response: str, expected: Dict[str, Any]) -> float:
    """
    완전성 계산

    - 응답 길이가 충분히 긴지 여부 + 필수 도구 사용 여부를 기반으로 점수를 계산한다.
    """
    completeness = 0.0
    
    # 응답 길이 점수 (최소 50자 이상)
    if len(response) >= 50:
        completeness += 0.5
    
    # 도구 사용 확인
    required_tools = expected.get("requiredTools", [])
    if not required_tools:
        completeness += 0.5
    else:
        # 실제로는 Agent 응답에서 도구 사용 여부 확인
        completeness += 0.3
    
    return min(completeness, 1.0)


def evaluate_response(response: Dict[str, Any], expected: Dict[str, Any], metrics: List[str]) -> Dict[str, float]:
    """
    응답 평가

    - metrics 리스트(accuracy, relevance, ...)에 명시된 항목에 대해서만
      개별 메트릭 함수를 호출해 결과를 딕셔너리로 돌려준다.
    """
    response_text = response.get("response", "")
    
    evaluation_results = {}
    
    if "accuracy" in metrics:
        evaluation_results["accuracy"] = calculate_accuracy(response_text, expected)
    
    if "relevance" in metrics:
        evaluation_results["relevance"] = calculate_relevance(response_text, expected)
    
    if "completeness" in metrics:
        evaluation_results["completeness"] = calculate_completeness(response_text, expected)
    
    if "responseTime" in metrics:
        # 응답 시간은 invoke_agent에서 측정
        evaluation_results["responseTime"] = response.get("response_time", 0.0)
    
    if "toolUsageCorrectness" in metrics:
        # 도구 사용 정확도
        required_tools = set(expected.get("requiredTools", []))
        used_tools = set(response.get("tools_used", []))
        if required_tools:
            evaluation_results["toolUsageCorrectness"] = len(required_tools & used_tools) / len(required_tools)
        else:
            evaluation_results["toolUsageCorrectness"] = 1.0
    
    return evaluation_results


def meets_thresholds(results: List[Dict[str, Any]], thresholds: Dict[str, float]) -> bool:
    """임계값 충족 여부 확인"""
    for result in results:
        metrics = result.get("metrics", {})
        for metric_name, threshold in thresholds.items():
            if metric_name == "overall":
                continue
            if metric_name in metrics:
                if metrics[metric_name] < threshold:
                    return False
    
    # Overall 임계값 확인
    if "overall" in thresholds:
        overall_scores = []
        for result in results:
            metrics = result.get("metrics", {})
            if metrics:
                avg_score = sum(metrics.values()) / len(metrics)
                overall_scores.append(avg_score)
        
        if overall_scores:
            avg_overall = sum(overall_scores) / len(overall_scores)
            if avg_overall < thresholds["overall"]:
                return False
    
    return True


def run_evaluation(dataset_file: str, agent_dir: str) -> List[Dict[str, Any]]:
    """
    평가 실행

    - 데이터셋의 testCases 를 순회하면서
      Agent를 호출하고 각 케이스별 메트릭을 계산하여 결과 리스트를 반환한다.
    """
    # 데이터셋 로드
    with open(dataset_file, 'r', encoding='utf-8') as f:
        dataset = json.load(f)
    
    # Agent 정의 로드
    agent_def_file = os.path.join(agent_dir, "agent-definition.yaml")
    with open(agent_def_file, 'r', encoding='utf-8') as f:
        agent_def = yaml.safe_load(f)
    
    test_cases = dataset.get("testCases", [])
    evaluation_metrics = dataset.get("evaluationMetrics", [])
    
    print(f"Running evaluation on {len(test_cases)} test cases...")
    
    results = []
    
    for test_case in test_cases:
        test_id = test_case.get("id", "unknown")
        input_text = test_case.get("input", "")
        expected = test_case.get("expectedOutput", {})
        context = test_case.get("context", {})
        
        print(f"  Testing: {test_id}")
        
        # Agent 실행
        start_time = time.time()
        response = invoke_agent(agent_def, input_text, context)
        response_time = time.time() - start_time
        response["response_time"] = response_time
        
        # 평가 메트릭 계산
        metrics = evaluate_response(response, expected, evaluation_metrics)
        
        results.append({
            "testCaseId": test_id,
            "input": input_text,
            "expected": expected,
            "response": response,
            "metrics": metrics,
            "timestamp": datetime.now().isoformat()
        })
        
        print(f"    Metrics: {metrics}")
    
    return results


def generate_report(results: List[Dict[str, Any]], output_dir: str = "evaluation-results"):
    """
    평가 리포트 생성

    - results.json (머신 친화적)과 report.md (사람이 읽기 좋은 요약)를 함께 생성한다.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # JSON 결과 저장
    results_file = os.path.join(output_dir, "results.json")
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # 마크다운 리포트 생성
    report_file = os.path.join(output_dir, "report.md")
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# Evaluation Report\n\n")
        f.write(f"Generated at: {datetime.now().isoformat()}\n\n")
        
        # 요약 통계
        if results:
            all_metrics = {}
            for result in results:
                for metric_name, value in result.get("metrics", {}).items():
                    if metric_name not in all_metrics:
                        all_metrics[metric_name] = []
                    all_metrics[metric_name].append(value)
            
            f.write("## Summary Statistics\n\n")
            for metric_name, values in all_metrics.items():
                avg = sum(values) / len(values)
                f.write(f"- **{metric_name}**: {avg:.3f} (avg)\n")
            f.write("\n")
        
        # 상세 결과
        f.write("## Detailed Results\n\n")
        for result in results:
            f.write(f"### Test Case: {result['testCaseId']}\n\n")
            f.write(f"**Input**: {result['input']}\n\n")
            f.write(f"**Metrics**:\n")
            for metric_name, value in result.get("metrics", {}).items():
                f.write(f"- {metric_name}: {value:.3f}\n")
            f.write("\n")
    
    print(f"✓ Evaluation report generated: {report_file}")


def main():
    parser = argparse.ArgumentParser(description="Run Agent Evaluation")
    parser.add_argument("--dataset", required=True, help="Evaluation dataset JSON file")
    parser.add_argument("--agent", required=True, help="Agent directory")
    
    args = parser.parse_args()
    
    try:
        results = run_evaluation(args.dataset, args.agent)
        generate_report(results)
        
        # 데이터셋에서 임계값 확인
        with open(args.dataset, 'r', encoding='utf-8') as f:
            dataset = json.load(f)
        
        thresholds = dataset.get("thresholds", {})
        if thresholds:
            if not meets_thresholds(results, thresholds):
                print("✗ Evaluation failed: metrics below threshold")
                sys.exit(1)
        
        print("✓ Evaluation completed successfully")
    except Exception as e:
        print(f"✗ Evaluation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
