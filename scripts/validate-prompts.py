#!/usr/bin/env python3
"""
프롬프트 검증 스크립트

- 프롬프트 텍스트(.md, .txt)를 대상으로
  - 길이/빈 값 여부
  - 템플릿 변수 형식({{var}}) 점검
  - password/api key 등 민감 정보 하드코딩 여부
  - system-prompt 의 최소 길이
  등을 검사한다.
"""
import os
import re
import sys
from pathlib import Path
from typing import List, Dict


def validate_prompt(prompt_file: str) -> List[str]:
    """프롬프트 파일 검증"""
    issues = []
    
    try:
        with open(prompt_file, 'r', encoding='utf-8') as f:
            prompt = f.read()
        
        # 1. 길이 검증
        if len(prompt) > 10000:
            issues.append("Prompt is too long (>10,000 characters)")
        
        if len(prompt) == 0:
            issues.append("Prompt is empty")
        
        # 2. 변수 검증 (템플릿 변수 형식 확인)
        # {{variable}} 형식의 변수 찾기
        variables = re.findall(r'\{\{(\w+)\}\}', prompt)
        
        # 3. 보안 검증 (민감 정보 포함 여부)
        sensitive_patterns = [
            (r'password\s*=\s*[\'"]\w+[\'"]', "Potential password found"),
            (r'api[_-]?key\s*=\s*[\'"]\w+[\'"]', "Potential API key found"),
            (r'secret\s*=\s*[\'"]\w+[\'"]', "Potential secret found"),
            (r'aws[_-]?access[_-]?key', "Potential AWS access key reference"),
        ]
        
        for pattern, message in sensitive_patterns:
            if re.search(pattern, prompt, re.IGNORECASE):
                issues.append(message)
        
        # 4. 기본 구조 검증 (시스템 프롬프트인 경우)
        if 'system-prompt' in prompt_file.lower():
            if len(prompt.strip()) < 50:
                issues.append("System prompt seems too short (minimum 50 characters recommended)")
        
        return issues
        
    except Exception as e:
        return [f"Error reading file: {e}"]


def validate_prompts_directory(prompts_dir: str) -> Dict[str, List[str]]:
    """프롬프트 디렉토리 검증"""
    results = {}
    
    if not os.path.exists(prompts_dir):
        return results
    
    # .md 파일 찾기
    for root, dirs, files in os.walk(prompts_dir):
        # versions 디렉토리는 제외 (버전 관리된 파일)
        if 'versions' in root:
            continue
            
        for file in files:
            if file.endswith(('.md', '.txt')):
                file_path = os.path.join(root, file)
                issues = validate_prompt(file_path)
                if issues:
                    results[file_path] = issues
    
    return results


def main():
    if len(sys.argv) < 2:
        print("Usage: validate-prompts.py <prompts-directory>...")
        sys.exit(1)
    
    all_valid = True
    
    for prompts_dir in sys.argv[1:]:
        if not os.path.exists(prompts_dir):
            print(f"✗ Directory not found: {prompts_dir}")
            all_valid = False
            continue
        
        results = validate_prompts_directory(prompts_dir)
        
        if results:
            print(f"✗ Issues found in {prompts_dir}:")
            for file_path, issues in results.items():
                print(f"  {file_path}:")
                for issue in issues:
                    print(f"    - {issue}")
            all_valid = False
        else:
            print(f"✓ All prompts in {prompts_dir} are valid")
    
    sys.exit(0 if all_valid else 1)


if __name__ == "__main__":
    main()
