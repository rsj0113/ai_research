"""
Step 1: Langfuse decorator API — 가장 빠르게 tracing 시작하는 법.
langfuse.openai 래퍼를 쓰면 OpenAI 호출이 자동으로 generation으로 기록됨.
"""

import os
from dotenv import load_dotenv
from langfuse import observe, get_client
from langfuse.openai import openai  # Langfuse가 감싼 OpenAI 클라이언트
from rich.console import Console

load_dotenv("../../.env")
console = Console()

lf = get_client()
client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])


@observe()
def generate_answer(question: str) -> str:
    """@observe()가 이 함수 전체를 span으로 기록. OpenAI 호출은 자동으로 generation으로 기록."""
    lf.update_current_span(metadata={"experiment": "basic-tracing"})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": question}],
        max_tokens=512,
    )
    return response.choices[0].message.content


@observe()
def rag_pipeline(question: str) -> str:
    """RAG 시뮬레이션 — 검색 span + generation이 자동으로 중첩 기록됨."""
    retrieved = f"[검색된 문서] {question}에 관한 관련 내용..."
    prompt = f"다음 컨텍스트를 바탕으로 답해줘.\n컨텍스트: {retrieved}\n질문: {question}"

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=512,
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    questions = [
        "Transformer 아키텍처의 핵심 혁신은 무엇인가요?",
        "RAG와 fine-tuning 중 어떤 걸 언제 써야 하나요?",
    ]

    for q in questions:
        console.print(f"\n[bold blue]Q:[/bold blue] {q}")
        answer = generate_answer(q)
        console.print(f"[green]A:[/green] {answer[:200]}...")

    lf.flush()
    console.print("\n[dim]→ cloud.langfuse.com 에서 trace 확인하세요[/dim]")
