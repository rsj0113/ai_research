"""
Step 1: Bedrock Guardrail 생성
- 콘텐츠 필터 (폭력, 혐오)
- PII 마스킹 (이메일, 전화번호)
- 차단 주제 (투자 조언)

실행 후 출력된 guardrailId와 guardrailVersion을 .env에 저장해둘 것.
"""

import os
import json
import boto3
from dotenv import load_dotenv
from rich.console import Console
from rich.syntax import Syntax

load_dotenv("../../.env")
console = Console()

bedrock = boto3.client(
    "bedrock",
    region_name=os.environ.get("AWS_DEFAULT_REGION", "us-east-1"),
)


def create_guardrail():
    response = bedrock.create_guardrail(
        name="ai-research-guardrail",
        description="실험용 가드레일: 콘텐츠 필터 + PII + 차단 주제",

        # 콘텐츠 필터: 폭력/혐오를 MEDIUM 이상에서 차단
        contentPolicyConfig={
            "filtersConfig": [
                {"type": "VIOLENCE", "inputStrength": "MEDIUM", "outputStrength": "MEDIUM"},
                {"type": "HATE", "inputStrength": "MEDIUM", "outputStrength": "MEDIUM"},
                {"type": "INSULTS", "inputStrength": "LOW", "outputStrength": "LOW"},
                {"type": "PROMPT_ATTACK", "inputStrength": "HIGH", "outputStrength": "NONE"},
            ]
        },

        # 차단 주제: 투자/금융 조언
        topicPolicyConfig={
            "topicsConfig": [
                {
                    "name": "investment-advice",
                    "definition": "특정 주식, 암호화폐, 금융 상품에 대한 투자 추천이나 매수/매도 조언",
                    "examples": [
                        "삼성전자 지금 사야 하나요?",
                        "비트코인 투자 추천해줘",
                        "어떤 ETF가 좋을까요?",
                    ],
                    "type": "DENY",
                }
            ]
        },

        # PII 감지 및 마스킹
        sensitiveInformationPolicyConfig={
            "piiEntitiesConfig": [
                {"type": "EMAIL", "action": "ANONYMIZE"},
                {"type": "PHONE", "action": "ANONYMIZE"},
                {"type": "NAME", "action": "ANONYMIZE"},
                {"type": "US_SOCIAL_SECURITY_NUMBER", "action": "BLOCK"},
            ],
            # 사내 사번 패턴 예시 (EMP-12345 형태)
            "regexesConfig": [
                {
                    "name": "employee-id",
                    "description": "사내 사번 패턴",
                    "pattern": r"EMP-\d{5}",
                    "action": "ANONYMIZE",
                }
            ],
        },

        # 차단 시 사용자에게 보여줄 메시지
        blockedInputMessaging="요청하신 내용은 처리할 수 없습니다.",
        blockedOutputsMessaging="응답을 제공할 수 없습니다.",
    )

    guardrail_id = response["guardrailId"]
    guardrail_version = response["version"]

    console.print(f"\n[bold green]✓ Guardrail 생성 완료[/bold green]")
    console.print(f"  ID     : [cyan]{guardrail_id}[/cyan]")
    console.print(f"  Version: [cyan]{guardrail_version}[/cyan]")
    console.print("\n[dim].env에 아래 줄 추가:[/dim]")
    console.print(f"[dim]BEDROCK_GUARDRAIL_ID={guardrail_id}[/dim]")
    console.print(f"[dim]BEDROCK_GUARDRAIL_VERSION={guardrail_version}[/dim]")

    return guardrail_id, guardrail_version


if __name__ == "__main__":
    create_guardrail()
