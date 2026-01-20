#!/usr/bin/env python3
"""
Agent 빌드 스크립트
"""
import yaml
import json
import os
import argparse
import shutil
from pathlib import Path
from typing import Dict, Any


def load_prompt(prompt_path: str, agent_dir: str) -> str:
    """프롬프트 파일 로드"""
    full_path = os.path.join(agent_dir, prompt_path)
    if not os.path.exists(full_path):
        raise FileNotFoundError(f"Prompt file not found: {full_path}")
    
    with open(full_path, 'r', encoding='utf-8') as f:
        return f.read()


def build_action_groups(tools: list) -> list:
    """도구 정의를 Action Groups로 변환"""
    action_groups = []
    
    for tool in tools:
        action_group = {
            "actionGroupName": tool["name"],
            "actionGroupExecutor": "LAMBDA" if tool["type"] == "function" else "API",
        }
        
        if tool["type"] == "api":
            action_group["apiSchema"] = {
                "payload": tool.get("endpoint", "")
            }
        
        action_groups.append(action_group)
    
    return action_groups


def build_knowledge_bases(kb_config: Dict[str, Any]) -> list:
    """Knowledge Base 설정을 Bedrock 형식으로 변환"""
    if not kb_config.get("enabled", False):
        return []
    
    kb_list = []
    
    if "dataSources" in kb_config:
        for ds in kb_config["dataSources"]:
            kb = {
                "dataSource": {
                    "type": ds["type"].upper(),
                }
            }
            
            if ds["type"] == "s3":
                kb["dataSource"]["s3Configuration"] = {
                    "bucketArn": f"arn:aws:s3:::{ds['bucket']}",
                    "inclusionPrefixes": [ds.get("path", "")]
                }
            
            kb_list.append(kb)
    
    return kb_list


def build_aws_agent(agent_def: Dict[str, Any], agent_dir: str, output_dir: str):
    """AWS Bedrock Agent 형식으로 빌드"""
    metadata = agent_def["metadata"]
    spec = agent_def["spec"]
    
    # System prompt 로드
    system_prompt = ""
    if "prompts" in spec and "systemPrompt" in spec["prompts"]:
        system_prompt = load_prompt(spec["prompts"]["systemPrompt"], agent_dir)
    
    bedrock_config = {
        "agentName": metadata["name"],
        "foundationModel": spec["foundationModel"]["modelId"],
        "instruction": system_prompt,
        "actionGroups": build_action_groups(spec.get("tools", [])),
        "knowledgeBases": build_knowledge_bases(spec.get("knowledgeBase", {}))
    }
    
    # 출력 디렉토리 생성
    os.makedirs(output_dir, exist_ok=True)
    
    # Bedrock Agent 설정 파일 저장
    config_file = os.path.join(output_dir, "bedrock-agent-config.json")
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(bedrock_config, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Built AWS Bedrock agent config: {config_file}")


def build_azure_agent(agent_def: Dict[str, Any], agent_dir: str, output_dir: str):
    """Azure OpenAI Assistant 형식으로 빌드"""
    metadata = agent_def["metadata"]
    spec = agent_def["spec"]
    
    # System prompt 로드
    system_prompt = ""
    if "prompts" in spec and "systemPrompt" in spec["prompts"]:
        system_prompt = load_prompt(spec["prompts"]["systemPrompt"], agent_dir)
    
    azure_config = {
        "name": metadata["name"],
        "model": spec["foundationModel"]["modelId"],
        "instructions": system_prompt,
        "tools": []
    }
    
    # 도구 변환
    for tool in spec.get("tools", []):
        tool_def = {
            "type": "function" if tool["type"] == "function" else "code_interpreter"
        }
        azure_config["tools"].append(tool_def)
    
    # 출력 디렉토리 생성
    os.makedirs(output_dir, exist_ok=True)
    
    # Azure Assistant 설정 파일 저장
    config_file = os.path.join(output_dir, "azure-assistant-config.json")
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(azure_config, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Built Azure Assistant config: {config_file}")


def build_gcp_agent(agent_def: Dict[str, Any], agent_dir: str, output_dir: str):
    """GCP Vertex AI Agent 형식으로 빌드"""
    metadata = agent_def["metadata"]
    spec = agent_def["spec"]
    
    # System prompt 로드
    system_prompt = ""
    if "prompts" in spec and "systemPrompt" in spec["prompts"]:
        system_prompt = load_prompt(spec["prompts"]["systemPrompt"], agent_dir)
    
    gcp_config = {
        "displayName": metadata["name"],
        "defaultLanguageCode": "ko",
        "timeZone": "Asia/Seoul",
        "description": metadata.get("description", ""),
        "enableLogging": True,
        "enableStackdriverLogging": True
    }
    
    # 출력 디렉토리 생성
    os.makedirs(output_dir, exist_ok=True)
    
    # GCP Agent 설정 파일 저장
    config_file = os.path.join(output_dir, "gcp-agent-config.json")
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(gcp_config, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Built GCP Vertex AI agent config: {config_file}")


def build_agent(agent_dir: str, output_dir: str = "build"):
    """Agent 빌드 메인 함수"""
    agent_def_file = os.path.join(agent_dir, "agent-definition.yaml")
    
    if not os.path.exists(agent_def_file):
        raise FileNotFoundError(f"Agent definition not found: {agent_def_file}")
    
    # Agent 정의 로드
    with open(agent_def_file, 'r', encoding='utf-8') as f:
        agent_def = yaml.safe_load(f)
    
    # Agent 이름으로 출력 디렉토리 생성
    agent_name = agent_def["metadata"]["name"]
    agent_output_dir = os.path.join(output_dir, agent_name)
    os.makedirs(agent_output_dir, exist_ok=True)
    
    # CSP별 빌드
    provider = agent_def["spec"]["foundationModel"]["provider"]
    
    if provider == "aws":
        build_aws_agent(agent_def, agent_dir, agent_output_dir)
    elif provider == "azure":
        build_azure_agent(agent_def, agent_dir, agent_output_dir)
    elif provider == "gcp":
        build_gcp_agent(agent_def, agent_dir, agent_output_dir)
    else:
        raise ValueError(f"Unsupported provider: {provider}")
    
    # 추가 파일 복사 (필요한 경우)
    # 프롬프트 파일, 도구 정의 등


def main():
    parser = argparse.ArgumentParser(description="Build AI Agent artifacts")
    parser.add_argument("--agent-dir", required=True, help="Agent directory path")
    parser.add_argument("--output-dir", default="build", help="Output directory")
    
    args = parser.parse_args()
    
    try:
        build_agent(args.agent_dir, args.output_dir)
        print("✓ Agent build completed successfully")
    except Exception as e:
        print(f"✗ Build failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    import sys
    main()
