#!/usr/bin/env python3
"""
도구 정의 검증 스크립트

- agents/*/tools/tool-definitions.yaml 내 각 tool 이
  - name / description 등의 필수 필드를 가지고 있는지
  - parameters 항목에 name/type 이 빠지지 않았는지
  등을 정적으로 검사한다.
"""
import yaml
import os
import sys
from pathlib import Path
from typing import Dict, Any, List


def validate_tool_definition(tool_def: Dict[str, Any], tool_name: str) -> List[str]:
    """도구 정의 검증"""
    issues = []
    
    # 필수 필드 검증
    required_fields = ["name", "description"]
    for field in required_fields:
        if field not in tool_def:
            issues.append(f"Missing required field: {field}")
    
    # parameters 검증
    if "parameters" in tool_def:
        for param in tool_def["parameters"]:
            if "name" not in param:
                issues.append("Parameter missing 'name' field")
            if "type" not in param:
                issues.append(f"Parameter '{param.get('name', 'unknown')}' missing 'type' field")
    
    return issues


def validate_tools_file(tools_file: str) -> bool:
    """도구 정의 파일 검증"""
    try:
        with open(tools_file, 'r', encoding='utf-8') as f:
            tools_data = yaml.safe_load(f)
        
        if not tools_data or "tools" not in tools_data:
            print(f"✗ {tools_file}: Missing 'tools' key")
            return False
        
        all_valid = True
        for tool_name, tool_def in tools_data["tools"].items():
            issues = validate_tool_definition(tool_def, tool_name)
            if issues:
                print(f"✗ {tools_file} - Tool '{tool_name}':")
                for issue in issues:
                    print(f"  - {issue}")
                all_valid = False
        
        if all_valid:
            print(f"✓ {tools_file} is valid")
        
        return all_valid
        
    except yaml.YAMLError as e:
        print(f"✗ {tools_file}: YAML parsing error: {e}")
        return False
    except Exception as e:
        print(f"✗ {tools_file}: Error: {e}")
        return False


def main():
    if len(sys.argv) < 2:
        print("Usage: validate-tools.py <tool-definitions.yaml>...")
        sys.exit(1)
    
    files = sys.argv[1:]
    all_valid = all(validate_tools_file(f) for f in files)
    sys.exit(0 if all_valid else 1)


if __name__ == "__main__":
    main()
