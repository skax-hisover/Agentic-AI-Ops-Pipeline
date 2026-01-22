#!/usr/bin/env python3
"""
평가 결과 비교 스크립트

- 최근 평가 결과(results.json)를 이전 베이스라인(baseline.json)과 비교하여
  메트릭별로 얼마나 개선/악화/유지되었는지를 출력한다.

첫 실행 시에는 현재 결과를 baseline.json 으로 저장하고,
그 이후부터는 기준점 대비 상대적인 변화를 보는 용도로 사용한다.
"""
import json
import os
import glob
from typing import Dict, Any, Optional


def load_baseline_results() -> Optional[Dict[str, Any]]:
    """베이스라인 결과 로드"""
    baseline_file = "evaluation-results/baseline.json"
    
    if not os.path.exists(baseline_file):
        return None
    
    with open(baseline_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def compare_results(current: Dict[str, Any], baseline: Dict[str, Any]) -> Dict[str, Any]:
    """결과 비교"""
    comparison = {
        "improved": [],
        "degraded": [],
        "unchanged": []
    }
    
    # 메트릭별 비교
    current_metrics = {}
    baseline_metrics = {}
    
    # 현재 결과에서 메트릭 추출
    if "results" in current:
        for result in current["results"]:
            for metric_name, value in result.get("metrics", {}).items():
                if metric_name not in current_metrics:
                    current_metrics[metric_name] = []
                current_metrics[metric_name].append(value)
    
    # 베이스라인 결과에서 메트릭 추출
    if "results" in baseline:
        for result in baseline["results"]:
            for metric_name, value in result.get("metrics", {}).items():
                if metric_name not in baseline_metrics:
                    baseline_metrics[metric_name] = []
                baseline_metrics[metric_name].append(value)
    
    # 메트릭 비교
    all_metrics = set(current_metrics.keys()) | set(baseline_metrics.keys())
    
    for metric_name in all_metrics:
        if metric_name in current_metrics and metric_name in baseline_metrics:
            current_avg = sum(current_metrics[metric_name]) / len(current_metrics[metric_name])
            baseline_avg = sum(baseline_metrics[metric_name]) / len(baseline_metrics[metric_name])
            
            diff = current_avg - baseline_avg
            diff_pct = (diff / baseline_avg * 100) if baseline_avg > 0 else 0
            
            if diff > 0.01:  # 1% 이상 개선
                comparison["improved"].append({
                    "metric": metric_name,
                    "current": current_avg,
                    "baseline": baseline_avg,
                    "improvement": diff_pct
                })
            elif diff < -0.01:  # 1% 이상 저하
                comparison["degraded"].append({
                    "metric": metric_name,
                    "current": current_avg,
                    "baseline": baseline_avg,
                    "degradation": abs(diff_pct)
                })
            else:
                comparison["unchanged"].append({
                    "metric": metric_name,
                    "current": current_avg,
                    "baseline": baseline_avg
                })
    
    return comparison


def main():
    # 현재 결과 로드
    current_file = "evaluation-results/results.json"
    if not os.path.exists(current_file):
        print("Current evaluation results not found")
        return
    
    with open(current_file, 'r', encoding='utf-8') as f:
        current_results = {"results": json.load(f)}
    
    # 베이스라인 결과 로드
    baseline_results = load_baseline_results()
    
    if not baseline_results:
        print("Baseline results not found. Saving current results as baseline...")
        os.makedirs("evaluation-results", exist_ok=True)
        with open("evaluation-results/baseline.json", 'w', encoding='utf-8') as f:
            json.dump(current_results, f, indent=2, ensure_ascii=False)
        print("✓ Baseline saved")
        return
    
    # 결과 비교
    comparison = compare_results(current_results, baseline_results)
    
    # 비교 결과 출력
    print("\n## Evaluation Results Comparison\n")
    
    if comparison["improved"]:
        print("### Improved Metrics:\n")
        for item in comparison["improved"]:
            print(f"- **{item['metric']}**: {item['current']:.3f} (baseline: {item['baseline']:.3f}, +{item['improvement']:.1f}%)")
        print()
    
    if comparison["degraded"]:
        print("### Degraded Metrics:\n")
        for item in comparison["degraded"]:
            print(f"- **{item['metric']}**: {item['current']:.3f} (baseline: {item['baseline']:.3f}, -{item['degradation']:.1f}%)")
        print()
    
    if comparison["unchanged"]:
        print("### Unchanged Metrics:\n")
        for item in comparison["unchanged"]:
            print(f"- **{item['metric']}**: {item['current']:.3f} (baseline: {item['baseline']:.3f})")
        print()


if __name__ == "__main__":
    main()
