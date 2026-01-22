#!/usr/bin/env python3
"""
프롬프트 버전 관리 스크립트

프롬프트 파일의 버전을 생성하고 관리합니다.
Git 태그와 함께 버전별 프롬프트 파일을 versions/ 디렉토리에 저장합니다.
"""
import os
import yaml
import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any


def create_prompt_version(prompt_file: str, version: str, agent_dir: str):
    """
    프롬프트 버전 생성
    
    Args:
        prompt_file: 프롬프트 파일 경로 (예: prompts/system-prompt.md)
        version: 버전 번호 (예: v1.2.0)
        agent_dir: Agent 디렉토리 경로
    """
    # 프롬프트 파일 읽기
    full_prompt_path = os.path.join(agent_dir, prompt_file)
    if not os.path.exists(full_prompt_path):
        raise FileNotFoundError(f"Prompt file not found: {full_prompt_path}")
    
    with open(full_prompt_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 버전 디렉토리에 저장
    version_dir = os.path.join(agent_dir, "prompts", "versions", version)
    os.makedirs(version_dir, exist_ok=True)
    
    # 프롬프트 파일명 추출
    prompt_filename = os.path.basename(prompt_file)
    version_file = os.path.join(version_dir, prompt_filename)
    
    with open(version_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ Created version {version} for {prompt_file}")
    return version_file


def create_version_metadata(agent_dir: str, version: str, prompt_files: list, commit_hash: str = None, description: str = None):
    """
    버전 메타데이터 생성
    
    Args:
        agent_dir: Agent 디렉토리 경로
        version: 버전 번호
        prompt_files: 버전이 생성된 프롬프트 파일 목록
        commit_hash: Git 커밋 해시 (선택)
        description: 버전 설명 (선택)
    """
    version_dir = os.path.join(agent_dir, "prompts", "versions", version)
    os.makedirs(version_dir, exist_ok=True)
    
    metadata = {
        "version": version,
        "files": prompt_files,
        "createdAt": datetime.now().isoformat(),
    }
    
    if commit_hash:
        metadata["commit"] = commit_hash
    
    if description:
        metadata["description"] = description
    
    metadata_file = os.path.join(version_dir, "metadata.yaml")
    with open(metadata_file, 'w', encoding='utf-8') as f:
        yaml.dump(metadata, f, default_flow_style=False, allow_unicode=True)
    
    print(f"✓ Created metadata: {metadata_file}")
    return metadata_file


def get_current_prompt_version(agent_dir: str) -> str:
    """
    agent-definition.yaml에서 현재 프롬프트 버전 확인
    
    Args:
        agent_dir: Agent 디렉토리 경로
    
    Returns:
        현재 프롬프트 버전 (예: v1.2.0)
    """
    agent_def_file = os.path.join(agent_dir, "agent-definition.yaml")
    
    if not os.path.exists(agent_def_file):
        raise FileNotFoundError(f"Agent definition not found: {agent_def_file}")
    
    with open(agent_def_file, 'r', encoding='utf-8') as f:
        agent_def = yaml.safe_load(f)
    
    if "spec" in agent_def and "prompts" in agent_def["spec"]:
        return agent_def["spec"]["prompts"].get("version", "v1.0.0")
    
    return "v1.0.0"


def main():
    parser = argparse.ArgumentParser(description="Manage prompt versions")
    parser.add_argument("--agent-dir", required=True, help="Agent directory path")
    parser.add_argument("--version", help="Version number (e.g., v1.2.0). If not provided, uses current version from agent-definition.yaml")
    parser.add_argument("--commit", help="Git commit hash")
    parser.add_argument("--description", help="Version description")
    parser.add_argument("--create-git-tag", action="store_true", help="Create Git tag for this version")
    
    args = parser.parse_args()
    
    try:
        # 버전 확인
        if args.version:
            version = args.version
        else:
            version = get_current_prompt_version(args.agent_dir)
            print(f"Using version from agent-definition.yaml: {version}")
        
        # agent-definition.yaml에서 프롬프트 파일 목록 가져오기
        agent_def_file = os.path.join(args.agent_dir, "agent-definition.yaml")
        with open(agent_def_file, 'r', encoding='utf-8') as f:
            agent_def = yaml.safe_load(f)
        
        prompt_files = []
        if "spec" in agent_def and "prompts" in agent_def["spec"]:
            prompts = agent_def["spec"]["prompts"]
            
            if "systemPrompt" in prompts:
                prompt_files.append(prompts["systemPrompt"])
                create_prompt_version(prompts["systemPrompt"], version, args.agent_dir)
            
            if "userPromptTemplate" in prompts:
                prompt_files.append(prompts["userPromptTemplate"])
                create_prompt_version(prompts["userPromptTemplate"], version, args.agent_dir)
        
        if not prompt_files:
            print("No prompt files found in agent-definition.yaml")
            sys.exit(1)
        
        # 메타데이터 생성
        create_version_metadata(
            args.agent_dir,
            version,
            prompt_files,
            args.commit,
            args.description
        )
        
        # Git 태그 생성 (선택)
        if args.create_git_tag:
            try:
                import subprocess
                tag_name = f"prompts/{version}"
                subprocess.run(["git", "tag", tag_name], check=True)
                print(f"✓ Created Git tag: {tag_name}")
            except subprocess.CalledProcessError:
                print("⚠ Failed to create Git tag (may not be in a Git repository)")
            except ImportError:
                print("⚠ Git tag creation skipped (subprocess not available)")
        
        print(f"\n✓ Prompt version {version} created successfully")
        
    except Exception as e:
        print(f"✗ Failed to create prompt version: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
