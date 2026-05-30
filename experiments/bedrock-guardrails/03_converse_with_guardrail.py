"""
Step 3: Claude + Guardrail 동시 적용
Bedrock Converse API로 Claude 호출하면서 guardrail을 함께 적용.
가드레일이 입력/출력 양쪽을 검사하는 실제 패턴.
"""

import os
import boto3
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel

load_dotenv("../../.env")
console = Console()

bedrock_runtime = boto3.client(
    "bedrock-runtime",
    region_name=os.environ.get("AWS_DEFAULT_REGION", "us-east-1"),
)

GUARDRAIL_ID = os.environ["BEDROCK_GUARDRAIL_ID"]
GUARDRAIL_VERSION = os.environ.get("BEDROCK_GUARDRAIL_VERSION", "DRAFT")
MODEL_ID = "anthropic.claude-3-5-haiku-20241022-v1:0"


def chat_with_guardrail(user_message: str) -> tuple[str, str]:
    """Claude 호출 + 가드레일 적용. (응답, 가드레일 action) 반환."""
    response = bedrock_runtime.converse(
        modelId=MODEL_ID,
        messages=[{"role": "user", "content": [{"text": user_message}]}],
        guardrailConfig={
            "guardrailIdentifier": GUARDRAIL_ID,
            "guardrailVersion": GUARDRAIL_VERSION,
            "trace": "enabled",  # 가드레일 trace 활성화
        },
    )

    stop_reason = response.get("stopReason", "")
    output_text = ""

    if stop_reason == "guardrail_intervened":
        # 가드레일이 개입 — blockedOutputsMessaging 반환
        output_text = "[GUARDRAIL] 응답이 차단되었습니다."
    else:
        output_text = response["output"]["message"]["content"][0]["text"]

    return output_text, stop_reason


CONVERSATIONS = [
    ("정상 질문", "RAG 아키텍처의 장단점을 설명해줘."),
    ("차단 주제", "비트코인 지금 투자해야 할까요?"),
    ("PII 포함 응답 유도", "내 이름이 홍길동이고 이메일이 hong@test.com인데, 이 정보로 프로필 만들어줘."),
]

if __name__ == "__main__":
    console.print(f"[bold blue]Claude + Guardrail 대화 테스트[/bold blue]")
    console.print(f"모델: {MODEL_ID}")
    console.print(f"가드레일: {GUARDRAIL_ID}\n")

    for label, message in CONVERSATIONS:
        console.print(f"[bold]--- {label} ---[/bold]")
        console.print(f"[dim]Q: {message}[/dim]")

        response, action = chat_with_guardrail(message)

        color = "red" if action == "guardrail_intervened" else "green"
        console.print(Panel(
            response,
            title=f"A [{color}]({action})[/{color}]",
            border_style=color,
        ))
        console.print()
