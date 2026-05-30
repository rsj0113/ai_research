"""
Step 1: Langfuse decorator API — 가장 빠르게 tracing 시작하는 법.
실행 후 cloud.langfuse.com 대시보드에서 trace 확인.
"""

import os
from dotenv import load_dotenv
from langfuse.decorators import langfuse_context, observe
from langfuse.openai import openai  # Langfuse가 감싼 OpenAI 클라이언트
import anthropic
from rich.console import Console

load_dotenv("../../.env")
console = Console()

# Anthropic 클라이언트 (수동으로 trace에 기록)
anthropic_client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])


@observe()  # 이 데코레이터 하나로 함수 전체가 trace에 기록됨
def generate_answer(question: str) -> str:
    """질문에 답변 생성. 내부 LLM 호출도 자동으로 generation으로 기록."""

    # Langfuse에 현재 trace 메타데이터 추가
    langfuse_context.update_current_trace(
        name="Q&A pipeline",
        tags=["experiment", "basic-tracing"],
        metadata={"model": "claude-haiku-4-5"},
    )

    msg = anthropic_client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=512,
        messages=[{"role": "user", "content": question}],
    )
    answer = msg.content[0].text

    # 수동으로 LLM 호출 기록 (Anthropic은 자동 계측 미지원 시 이렇게)
    langfuse_context.update_current_observation(
        input=question,
        output=answer,
        usage={
            "input": msg.usage.input_tokens,
            "output": msg.usage.output_tokens,
        },
    )

    return answer


@observe()
def rag_pipeline(question: str) -> str:
    """RAG 파이프라인 시뮬레이션 — 검색 span + 생성 span이 중첩된 구조."""

    # 검색 단계 (실제론 vector DB 호출)
    with langfuse_context.current_span() if hasattr(langfuse_context, "current_span") else __import__("contextlib").nullcontext():
        retrieved_context = f"[검색된 문서] {question}에 관한 관련 내용..."

    # 생성 단계
    answer = generate_answer(f"다음 컨텍스트를 바탕으로 답해줘.\n컨텍스트: {retrieved_context}\n질문: {question}")
    return answer


if __name__ == "__main__":
    questions = [
        "Transformer 아키텍처의 핵심 혁신은 무엇인가요?",
        "RAG와 fine-tuning 중 어떤 걸 언제 써야 하나요?",
    ]

    for q in questions:
        console.print(f"\n[bold blue]Q:[/bold blue] {q}")
        answer = generate_answer(q)
        console.print(f"[green]A:[/green] {answer[:200]}...")

    console.print("\n[dim]→ cloud.langfuse.com 에서 trace 확인하세요[/dim]")
