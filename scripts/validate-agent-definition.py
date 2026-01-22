#!/usr/bin/env python3
"""
Agent 정의 스키마 검증 스크립트

- agents/*/agent-definition.yaml 이 프로젝트에서 정의한 최소 스키마를 만족하는지 확인하고
- prompts 경로에 실제 파일(system/user 템플릿)이 존재하는지도 함께 체크한다.

Build 파이프라인의 첫 단계(Validate Stage)에서 실행되는 핵심 검증 로직.
"""
import yaml
import json
import sys
import os
from pathlib import Path
from typing import Dict, Any, List

# Agent 정의 스키마
AGENT_SCHEMA = {
    "type": "object",
    "required": ["apiVersion", "kind", "metadata", "spec"],
    "properties": {
        "apiVersion": {"type": "string"},
        "kind": {"type": "string", "enum": ["Agent"]},
        "metadata": {
            "type": "object",
            "required": ["name", "version"],
            "properties": {
                "name": {"type": "string"},
                "version": {"type": "string"},
                "description": {"type": "string"}
            }
        },
        "spec": {
            "type": "object",
            "required": ["foundationModel"],
            "properties": {
                "foundationModel": {
                    "type": "object",
                    "required": ["provider", "modelId"],
                    "properties": {
                        "provider": {"type": "string", "enum": ["aws", "azure", "gcp"]},
                        "modelId": {"type": "string"},
                        "temperature": {"type": "number"},
                        "maxTokens": {"type": "integer"}
                    }
                },
                "prompts": {"type": "object"},
                "tools": {"type": "array"},
                "knowledgeBase": {"type": "object"},
                "security": {"type": "object"},
                "observability": {"type": "object"}
            }
        }
    }
}


def validate_schema(data: Dict[str, Any], schema: Dict[str, Any], path: str = "") -> List[str]:
    """간단한 스키마 검증 (jsonschema 대신 기본 검증)"""
    errors = []
    
    # 필수 필드 검증
    if "required" in schema:
        for field in schema["required"]:
            if field not in data:
                errors.append(f"{path}.{field} is required" if path else f"{field} is required")
    
    # 타입 검증
    if "type" in schema:
        expected_type = schema["type"]
        if expected_type == "object" and not isinstance(data, dict):
            errors.append(f"{path} must be an object")
        elif expected_type == "array" and not isinstance(data, list):
            errors.append(f"{path} must be an array")
        elif expected_type == "string" and not isinstance(data, str):
            errors.append(f"{path} must be a string")
        elif expected_type == "number" and not isinstance(data, (int, float)):
            errors.append(f"{path} must be a number")
        elif expected_type == "integer" and not isinstance(data, int):
            errors.append(f"{path} must be an integer")
    
    # Enum 검증
    if "enum" in schema and data not in schema["enum"]:
        errors.append(f"{path} must be one of {schema['enum']}")
    
    # 중첩 객체 검증
    if isinstance(data, dict) and "properties" in schema:
        for key, value in data.items():
            if key in schema["properties"]:
                sub_errors = validate_schema(
                    value,
                    schema["properties"][key],
                    f"{path}.{key}" if path else key
                )
                errors.extend(sub_errors)
    
    return errors


def validate_agent_definition(file_path: str) -> bool:
    """Agent 정의 파일 검증"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            agent_def = yaml.safe_load(f)
        
        if not agent_def:
            print(f"✗ {file_path}: File is empty")
            return False
        
        # 스키마 검증
        errors = validate_schema(agent_def, AGENT_SCHEMA)
        
        if errors:
            print(f"✗ {file_path} validation failed:")
            for error in errors:
                print(f"  - {error}")
            return False
        
        # 추가 검증: 파일 경로 존재 확인
        if "spec" in agent_def and "prompts" in agent_def["spec"]:
            prompts = agent_def["spec"]["prompts"]
            agent_dir = os.path.dirname(file_path)
            
            if "systemPrompt" in prompts:
                prompt_path = os.path.join(agent_dir, prompts["systemPrompt"])
                if not os.path.exists(prompt_path):
                    print(f"✗ {file_path}: System prompt file not found: {prompt_path}")
                    return False
            
            if "userPromptTemplate" in prompts:
                prompt_path = os.path.join(agent_dir, prompts["userPromptTemplate"])
                if not os.path.exists(prompt_path):
                    print(f"✗ {file_path}: User prompt template file not found: {prompt_path}")
                    return False
        
        print(f"✓ {file_path} is valid")
        return True
        
    except yaml.YAMLError as e:
        print(f"✗ {file_path}: YAML parsing error: {e}")
        return False
    except Exception as e:
        print(f"✗ {file_path}: Error: {e}")
        return False


def main():
    if len(sys.argv) < 2:
        print("Usage: validate-agent-definition.py <agent-definition.yaml>...")
        sys.exit(1)
    
    files = sys.argv[1:]
    all_valid = all(validate_agent_definition(f) for f in files)
    sys.exit(0 if all_valid else 1)


if __name__ == "__main__":
    main()
