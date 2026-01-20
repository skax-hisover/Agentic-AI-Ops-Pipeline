"""
Agent 정의 단위 테스트
"""
import pytest
import yaml
import os
from pathlib import Path


def test_agent_definition_exists():
    """Agent 정의 파일이 존재하는지 확인"""
    agent_dir = Path("agents/customer-support-agent")
    agent_def_file = agent_dir / "agent-definition.yaml"
    
    assert agent_def_file.exists(), "Agent definition file not found"


def test_agent_definition_structure():
    """Agent 정의 구조 검증"""
    agent_def_file = Path("agents/customer-support-agent/agent-definition.yaml")
    
    with open(agent_def_file, 'r', encoding='utf-8') as f:
        agent_def = yaml.safe_load(f)
    
    # 필수 필드 확인
    assert "apiVersion" in agent_def
    assert "kind" in agent_def
    assert "metadata" in agent_def
    assert "spec" in agent_def
    
    # Metadata 검증
    assert "name" in agent_def["metadata"]
    assert "version" in agent_def["metadata"]
    
    # Spec 검증
    assert "foundationModel" in agent_def["spec"]
    assert "provider" in agent_def["spec"]["foundationModel"]
    assert "modelId" in agent_def["spec"]["foundationModel"]


def test_prompt_files_exist():
    """프롬프트 파일이 존재하는지 확인"""
    agent_dir = Path("agents/customer-support-agent")
    
    system_prompt = agent_dir / "prompts" / "system-prompt.md"
    user_prompt = agent_dir / "prompts" / "user-prompt-template.md"
    
    assert system_prompt.exists(), "System prompt file not found"
    assert user_prompt.exists(), "User prompt template file not found"


def test_tool_definitions_exist():
    """도구 정의 파일이 존재하는지 확인"""
    tool_def_file = Path("agents/customer-support-agent/tools/tool-definitions.yaml")
    
    assert tool_def_file.exists(), "Tool definitions file not found"
    
    with open(tool_def_file, 'r', encoding='utf-8') as f:
        tools = yaml.safe_load(f)
    
    assert "tools" in tools, "Tools section not found in tool definitions"
