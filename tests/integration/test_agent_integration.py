"""
Agent 통합 테스트
"""
import pytest
import yaml
from pathlib import Path


@pytest.fixture
def agent_definition():
    """Agent 정의 로드"""
    agent_def_file = Path("agents/customer-support-agent/agent-definition.yaml")
    with open(agent_def_file, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def test_agent_definition_complete(agent_definition):
    """Agent 정의가 완전한지 확인"""
    assert agent_definition is not None
    assert "metadata" in agent_definition
    assert "spec" in agent_definition


def test_knowledge_base_config(agent_definition):
    """Knowledge Base 설정 검증"""
    if "knowledgeBase" in agent_definition.get("spec", {}):
        kb_config = agent_definition["spec"]["knowledgeBase"]
        
        if kb_config.get("enabled", False):
            assert "dataSources" in kb_config
            assert "embeddingModel" in kb_config
            assert "vectorStore" in kb_config


def test_security_config(agent_definition):
    """보안 설정 검증"""
    if "security" in agent_definition.get("spec", {}):
        security = agent_definition["spec"]["security"]
        
        if "guardrails" in security:
            guardrails = security["guardrails"]
            if guardrails.get("enabled", False):
                assert "contentFilter" in guardrails


def test_observability_config(agent_definition):
    """관찰성 설정 검증"""
    if "observability" in agent_definition.get("spec", {}):
        obs = agent_definition["spec"]["observability"]
        
        assert "logging" in obs or "metrics" in obs or "tracing" in obs
