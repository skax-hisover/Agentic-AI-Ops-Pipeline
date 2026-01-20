#!/usr/bin/env python3
"""
평가 리포트 생성 스크립트
"""
import json
import os
import glob
from datetime import datetime
from typing import List, Dict, Any


def load_evaluation_results(results_dir: str = "evaluation-results") -> List[Dict[str, Any]]:
    """평가 결과 로드"""
    results_file = os.path.join(results_dir, "results.json")
    
    if not os.path.exists(results_file):
        print(f"Results file not found: {results_file}")
        return []
    
    with open(results_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def generate_summary_report(results: List[Dict[str, Any]], output_file: str = "evaluation-results/report.md"):
    """요약 리포트 생성"""
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Agent Evaluation Report\n\n")
        f.write(f"Generated at: {datetime.now().isoformat()}\n\n")
        
        if not results:
            f.write("No evaluation results found.\n")
            return
        
        # 전체 통계
        all_metrics = {}
        for result in results:
            for metric_name, value in result.get("metrics", {}).items():
                if metric_name not in all_metrics:
                    all_metrics[metric_name] = []
                all_metrics[metric_name].append(value)
        
        f.write("## Overall Statistics\n\n")
        f.write("| Metric | Average | Min | Max |\n")
        f.write("|--------|---------|-----|-----|\n")
        
        for metric_name, values in all_metrics.items():
            avg = sum(values) / len(values)
            min_val = min(values)
            max_val = max(values)
            f.write(f"| {metric_name} | {avg:.3f} | {min_val:.3f} | {max_val:.3f} |\n")
        
        f.write("\n")
        
        # 테스트 케이스별 결과
        f.write("## Test Case Results\n\n")
        for result in results:
            test_id = result.get("testCaseId", "unknown")
            f.write(f"### {test_id}\n\n")
            f.write(f"**Input**: {result.get('input', 'N/A')}\n\n")
            f.write("**Metrics**:\n\n")
            
            metrics = result.get("metrics", {})
            for metric_name, value in metrics.items():
                f.write(f"- {metric_name}: **{value:.3f}**\n")
            
            f.write("\n")


def main():
    results = load_evaluation_results()
    generate_summary_report(results)
    print("✓ Evaluation report generated")


if __name__ == "__main__":
    main()
