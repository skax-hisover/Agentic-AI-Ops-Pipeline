#!/usr/bin/env python3
"""
보안 정책 검증 스크립트

- agent-definition.yaml 의 spec.security 섹션이 최소 요구 사항을 충족하는지 확인하고
- Agent 디렉터리 내 YAML/Python/JS/TS/Markdown 파일 전체를 스캔하여
  password/api key/secret 등 하드코딩된 자격 증명 패턴을 탐지한다.

보안 관점에서 Agent 정의와 구현이 기본 가이드를 따르고 있는지 점검하는 역할.
"""
import yaml
import os
import re
import sys
from pathlib import Path
from typing import Dict, Any, List


def check_security_policies(agent_dir: str) -> List[str]:
    """Agent 디렉토리의 보안 정책 검증"""
    issues = []
    
    agent_def_file = os.path.join(agent_dir, "agent-definition.yaml")
    if not os.path.exists(agent_def_file):
        return [f"Agent definition file not found: {agent_def_file}"]
    
    try:
        with open(agent_def_file, 'r', encoding='utf-8') as f:
            agent_def = yaml.safe_load(f)
        
        # Security 섹션 검증
        if "spec" in agent_def and "security" in agent_def["spec"]:
            security = agent_def["spec"]["security"]
            
            # Guardrails 검증
            if "guardrails" in security:
                guardrails = security["guardrails"]
                if guardrails.get("enabled", False):
                    if "contentFilter" not in guardrails:
                        issues.append("Guardrails enabled but contentFilter not specified")
                    if "piiDetection" not in guardrails:
                        issues.append("Guardrails enabled but piiDetection not specified")
            
            # Permissions 검증
            if "permissions" in security:
                for perm in security["permissions"]:
                    if "resource" not in perm:
                        issues.append("Permission missing 'resource' field")
                    if "actions" not in perm:
                        issues.append("Permission missing 'actions' field")
        else:
            issues.append("Security section not found in agent definition")
        
        # 하드코딩된 자격증명 검색
        for root, dirs, files in os.walk(agent_dir):
            for file in files:
                if file.endswith(('.yaml', '.yml', '.py', '.js', '.ts', '.md')):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # 민감한 패턴 검색
                        sensitive_patterns = [
                            (r'password\s*[:=]\s*[\'"]\w+[\'"]', "Hardcoded password"),
                            (r'api[_-]?key\s*[:=]\s*[\'"]\w+[\'"]', "Hardcoded API key"),
                            (r'secret\s*[:=]\s*[\'"]\w+[\'"]', "Hardcoded secret"),
                            (r'aws[_-]?access[_-]?key[_-]?id\s*[:=]\s*[\'"]\w+[\'"]', "Hardcoded AWS access key"),
                        ]
                        
                        for pattern, message in sensitive_patterns:
                            if re.search(pattern, content, re.IGNORECASE):
                                issues.append(f"{file_path}: {message}")
                    except:
                        pass
        
        return issues
        
    except Exception as e:
        return [f"Error checking security: {e}"]


def main():
    if len(sys.argv) < 2:
        print("Usage: check-security-policies.py <agent-directory>...")
        sys.exit(1)
    
    all_valid = True
    
    for agent_dir in sys.argv[1:]:
        if not os.path.exists(agent_dir):
            print(f"✗ Directory not found: {agent_dir}")
            all_valid = False
            continue
        
        issues = check_security_policies(agent_dir)
        
        if issues:
            print(f"✗ Security issues found in {agent_dir}:")
            for issue in issues:
                print(f"  - {issue}")
            all_valid = False
        else:
            print(f"✓ {agent_dir} security policies are valid")
    
    sys.exit(0 if all_valid else 1)


if __name__ == "__main__":
    main()
