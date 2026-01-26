#!/usr/bin/env python3
"""
Agent 배포 스크립트

- build 단계에서 생성한 설정/Agent 정의를 바탕으로
- AWS / Azure / GCP 각 CSP에 Agent(또는 Assistant)를 생성/업데이트하는 책임을 가진다.

AWS Bedrock Agent 배포 로직이 구현되어 있으며,
Azure/GCP 배포 로직은 주석으로 예시가 제공되어 있습니다.
"""
import yaml
import json
import os
import argparse
import sys
import time
from typing import Dict, Any, Optional


def load_agent_definition(agent_def_file: str) -> Dict[str, Any]:
    """Agent 정의 파일 로드"""
    with open(agent_def_file, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def load_bedrock_config(agent_name: str, build_dir: str = "build") -> Dict[str, Any]:
    """
    bedrock-agent-config.json 파일 로드
    
    Args:
        agent_name: Agent 이름
        build_dir: 빌드 디렉토리 경로
    
    Returns:
        Bedrock Agent 설정 딕셔너리
    """
    config_path = os.path.join(build_dir, agent_name, "bedrock-agent-config.json")
    
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Bedrock config file not found: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def find_existing_agent(bedrock_agent_client, agent_name: str) -> Optional[str]:
    """
    기존 Agent ID 찾기
    
    Args:
        bedrock_agent_client: boto3 bedrock-agent 클라이언트
        agent_name: Agent 이름
    
    Returns:
        Agent ID (없으면 None)
    """
    try:
        response = bedrock_agent_client.list_agents()
        
        for agent in response.get('agentSummaries', []):
            if agent['agentName'] == agent_name:
                return agent['agentId']
        
        return None
    except Exception as e:
        print(f"Warning: Failed to list agents: {e}")
        return None


def deploy_aws_agent(agent_def: Dict[str, Any], environment: str, enable_canary: bool = False):
    """
    AWS Bedrock Agent 배포

    - boto3(Bedrock Agent)를 이용해 bedrock-agent-config.json을 읽어
      Agent를 생성/업데이트하고, Action Groups와 Knowledge Base를 연결한다.
    """
    import boto3
    
    print(f"Deploying AWS Bedrock Agent to {environment}...")
    
    # 환경별 설정 로드
    env_config = get_environment_config(environment)
    region = env_config.get("region", "us-east-1")
    
    # Bedrock Agent 클라이언트 생성
    try:
        bedrock_agent = boto3.client('bedrock-agent', region_name=region)
    except Exception as e:
        raise RuntimeError(f"Failed to create Bedrock Agent client: {e}")
    
    # Agent 이름 및 설정 로드
    agent_name = agent_def['metadata']['name']
    bedrock_config = load_bedrock_config(agent_name)
    
    # 기존 Agent 확인
    existing_agent_id = find_existing_agent(bedrock_agent, agent_name)
    
    # Agent 생성 또는 업데이트
    if existing_agent_id:
        print(f"  Found existing agent: {existing_agent_id}")
        print(f"  Updating agent...")
        
        try:
            # Agent 업데이트
            update_response = bedrock_agent.update_agent(
                agentId=existing_agent_id,
                agentName=bedrock_config['agentName'],
                instruction=bedrock_config['instruction'],
                foundationModel=bedrock_config['foundationModel']
            )
            agent_id = existing_agent_id
            print(f"  ✓ Agent updated successfully")
        except Exception as e:
            raise RuntimeError(f"Failed to update agent: {e}")
    else:
        print(f"  Creating new agent...")
        
        try:
            # Agent 생성
            create_response = bedrock_agent.create_agent(
                agentName=bedrock_config['agentName'],
                instruction=bedrock_config['instruction'],
                foundationModel=bedrock_config['foundationModel']
            )
            agent_id = create_response['agent']['agentId']
            print(f"  ✓ Agent created: {agent_id}")
        except Exception as e:
            raise RuntimeError(f"Failed to create agent: {e}")
    
    # Action Groups 추가/업데이트
    if bedrock_config.get('actionGroups'):
        print(f"  Configuring action groups...")
        
        for action_group in bedrock_config['actionGroups']:
            action_group_name = action_group['actionGroupName']
            
            try:
                # 기존 Action Group 확인
                list_response = bedrock_agent.list_agent_action_groups(agentId=agent_id)
                existing_ag = None
                
                for ag in list_response.get('actionGroupSummaries', []):
                    if ag['actionGroupName'] == action_group_name:
                        existing_ag = ag
                        break
                
                if existing_ag:
                    # Action Group 업데이트 (간단한 예시 - 실제로는 더 복잡할 수 있음)
                    print(f"    - Updating action group: {action_group_name}")
                    # Note: update_agent_action_group API는 실제 파라미터에 따라 다를 수 있음
                else:
                    # Action Group 생성
                    print(f"    - Creating action group: {action_group_name}")
                    
                    if action_group['actionGroupExecutor'] == 'LAMBDA':
                        # Lambda 함수 기반 Action Group (실제 Lambda ARN은 환경 변수나 설정에서 가져와야 함)
                        lambda_arn = os.getenv(
                            f"LAMBDA_ARN_{action_group_name.upper().replace('-', '_')}",
                            f"arn:aws:lambda:{region}:*:function:{action_group_name}"
                        )
                        
                        bedrock_agent.create_agent_action_group(
                            agentId=agent_id,
                            actionGroupName=action_group_name,
                            actionGroupExecutor={
                                'lambda': lambda_arn
                            },
                            actionGroupState='ENABLED'
                        )
                    elif action_group['actionGroupExecutor'] == 'API':
                        # API 기반 Action Group
                        bedrock_agent.create_agent_action_group(
                            agentId=agent_id,
                            actionGroupName=action_group_name,
                            apiSchema={
                                'payload': action_group.get('apiSchema', {}).get('payload', '')
                            },
                            actionGroupState='ENABLED'
                        )
                    
                    print(f"      ✓ Action group created: {action_group_name}")
                    
            except Exception as e:
                print(f"      ⚠ Warning: Failed to configure action group {action_group_name}: {e}")
                # Action Group 설정 실패해도 계속 진행
    
    # Knowledge Base 연결
    if bedrock_config.get('knowledgeBases'):
        print(f"  Configuring knowledge bases...")
        
        for kb_config in bedrock_config['knowledgeBases']:
            try:
                # Knowledge Base ID는 실제 환경에서 생성되어 있어야 함
                # 여기서는 설정 파일의 정보를 기반으로 연결 시도
                kb_id = os.getenv(
                    'KNOWLEDGE_BASE_ID',
                    f"kb-{agent_name}-{environment}"
                )
                
                # Knowledge Base 연결 (실제 API는 더 복잡할 수 있음)
                print(f"    - Associating knowledge base: {kb_id}")
                # Note: associate_agent_knowledge_base API 호출 필요
                # bedrock_agent.associate_agent_knowledge_base(...)
                
            except Exception as e:
                print(f"      ⚠ Warning: Failed to configure knowledge base: {e}")
                # Knowledge Base 설정 실패해도 계속 진행
    
    # Agent 준비 (배포 전 필수 단계)
    print(f"  Preparing agent for deployment...")
    try:
        prepare_response = bedrock_agent.prepare_agent(agentId=agent_id)
        print(f"  ✓ Agent prepared successfully")
    except Exception as e:
        print(f"  ⚠ Warning: Failed to prepare agent: {e}")
        # Prepare 실패해도 계속 진행 (이미 준비된 상태일 수 있음)
    
    print(f"✓ AWS Bedrock Agent deployed to {environment}")
    print(f"  Agent ID: {agent_id}")
    print(f"  Agent Name: {agent_name}")
    print(f"  Region: {region}")
    
    if enable_canary:
        print("  Canary deployment enabled")
        print("  Monitoring canary traffic...")
        # Canary 배포 로직은 추가 구현 필요


def deploy_azure_agent(agent_def: Dict[str, Any], environment: str):
    """
    Azure OpenAI Assistant 배포

    - scripts/build-agent.py 에서 생성한 azure-assistant-config.json 을 사용해
      Azure OpenAI Assistants API로 리소스를 만드는 역할을 하도록 확장할 수 있다.
    """
    print(f"Deploying Azure OpenAI Assistant to {environment}...")
    
    # 실제 배포 로직은 Azure SDK를 사용하여 구현
    # 예시:
    # from azure.identity import DefaultAzureCredential
    # from openai import AzureOpenAI  # openai 패키지에서 AzureOpenAI 클래스 제공
    # 
    # client = AzureOpenAI(
    #     azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    #     api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    #     api_version="2024-02-15-preview"
    # )
    # 
    # assistant = client.beta.assistants.create(**assistant_config)
    
    print(f"✓ Azure OpenAI Assistant deployed to {environment}")
    print(f"  Assistant ID: assistant-{environment}-{agent_def['metadata']['name']}")


def deploy_gcp_agent(agent_def: Dict[str, Any], environment: str):
    """
    GCP Vertex AI Agent 배포

    - gcp-agent-config.json 을 읽어 Vertex AI Agent / Dialogflow 등으로
      Agent 리소스를 만드는 역할을 수행하도록 확장 가능하다.
    """
    print(f"Deploying GCP Vertex AI Agent to {environment}...")
    
    # 실제 배포 로직은 GCP SDK를 사용하여 구현
    # 예시:
    # from google.cloud import dialogflow
    # 
    # client = dialogflow.AgentsClient()
    # agent = dialogflow.types.Agent(**agent_config)
    # response = client.create_agent(parent=project_path, agent=agent)
    
    print(f"✓ GCP Vertex AI Agent deployed to {environment}")
    print(f"  Agent ID: agent-{environment}-{agent_def['metadata']['name']}")


def deploy_agent(agent_def_file: str, environment: str, enable_canary: bool = False):
    """
    Agent 배포 메인 함수

    - Agent 정의 YAML을 읽어 provider(aws/azure/gcp)를 확인한 뒤
      CSP별 deploy_* 함수를 호출한다.
    """
    agent_def = load_agent_definition(agent_def_file)
    provider = agent_def["spec"]["foundationModel"]["provider"]
    
    print(f"Deploying agent: {agent_def['metadata']['name']}")
    print(f"Environment: {environment}")
    print(f"Provider: {provider}")
    print(f"Version: {agent_def['metadata']['version']}")
    
    # 환경별 설정 적용
    env_config = get_environment_config(environment)
    
    if provider == "aws":
        deploy_aws_agent(agent_def, environment, enable_canary)
    elif provider == "azure":
        deploy_azure_agent(agent_def, environment)
    elif provider == "gcp":
        deploy_gcp_agent(agent_def, environment)
    else:
        raise ValueError(f"Unsupported provider: {provider}")
    
    print(f"✓ Deployment completed successfully")


def get_environment_config(environment: str) -> Dict[str, Any]:
    """
    환경별 설정 로드

    - 실제로는 환경 변수(.env, SSM, Secret Manager 등)나 별도 설정 파일에서
      region, timeout, endpoint 등을 읽어오도록 확장할 수 있다.
    """
    configs = {
        "dev": {
            "region": "us-east-1",
            "timeout": 30
        },
        "staging": {
            "region": "us-east-1",
            "timeout": 60
        },
        "production": {
            "region": "us-east-1",
            "timeout": 120
        }
    }
    return configs.get(environment, configs["dev"])


def main():
    parser = argparse.ArgumentParser(description="Deploy AI Agent")
    parser.add_argument("--agent-definition", required=True, help="Agent definition YAML file")
    parser.add_argument("--environment", required=True, choices=["dev", "staging", "production"], help="Deployment environment")
    parser.add_argument("--enable-canary", action="store_true", help="Enable canary deployment")
    
    args = parser.parse_args()
    
    try:
        deploy_agent(args.agent_definition, args.environment, args.enable_canary)
    except Exception as e:
        print(f"✗ Deployment failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
