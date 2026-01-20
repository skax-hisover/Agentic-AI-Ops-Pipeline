#!/usr/bin/env python3
"""
프롬프트 렌더링 테스트 스크립트
"""
import os
import re
import sys
from pathlib import Path
from typing import Dict, Any


def render_template(template: str, variables: Dict[str, Any]) -> str:
    """템플릿 변수 치환"""
    result = template
    
    # {{variable}} 형식의 변수 치환
    for key, value in variables.items():
        pattern = r'\{\{' + re.escape(key) + r'\}\}'
        result = re.sub(pattern, str(value), result)
    
    return result


def test_prompt_rendering(agent_dir: str) -> bool:
    """프롬프트 렌더링 테스트"""
    agent_def_file = os.path.join(agent_dir, "agent-definition.yaml")
    
    if not os.path.exists(agent_def_file):
        print(f"✗ Agent definition not found: {agent_def_file}")
        return False
    
    try:
        import yaml
        with open(agent_def_file, 'r', encoding='utf-8') as f:
            agent_def = yaml.safe_load(f)
        
        # User prompt template 로드
        if "spec" not in agent_def or "prompts" not in agent_def["spec"]:
            print("✗ Prompts section not found")
            return False
        
        prompts = agent_def["spec"]["prompts"]
        
        if "userPromptTemplate" not in prompts:
            print("✗ User prompt template not specified")
            return False
        
        template_path = os.path.join(agent_dir, prompts["userPromptTemplate"])
        if not os.path.exists(template_path):
            print(f"✗ Template file not found: {template_path}")
            return False
        
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()
        
        # 테스트 변수
        test_variables = {
            "user_input": "테스트 입력입니다",
            "context": {"user_id": "test_user", "session_id": "test_session"},
            "conversation_history": []
        }
        
        # 렌더링 테스트
        rendered = render_template(template, test_variables)
        
        # 렌더링 결과 검증
        if "{{" in rendered or "}}" in rendered:
            # 치환되지 않은 변수 확인
            remaining_vars = re.findall(r'\{\{(\w+)\}\}', rendered)
            if remaining_vars:
                print(f"✗ Unresolved variables: {remaining_vars}")
                return False
        
        print(f"✓ Prompt rendering test passed for {agent_dir}")
        return True
        
    except Exception as e:
        print(f"✗ Error testing prompt rendering: {e}")
        return False


def main():
    if len(sys.argv) < 2:
        # 기본적으로 모든 agent 테스트
        agent_dirs = [d for d in os.listdir("agents") if os.path.isdir(os.path.join("agents", d))]
        agent_dirs = [os.path.join("agents", d) for d in agent_dirs]
    else:
        agent_dirs = sys.argv[1:]
    
    all_passed = all(test_prompt_rendering(d) for d in agent_dirs)
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
