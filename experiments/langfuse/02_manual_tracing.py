"""
Step 2: Langfuse manual tracing — trace/span/generation을 코드로 직접 제어.
decorator API로 안 되는 세밀한 제어가 필요할 때 이 방식.
"""

import os
import time
from dotenv import load_dotenv
from langfuse import Langfuse
import anthropic
from rich.console import Console

load_dotenv("../../.env")
console = Console()

lf = Langfuse(
    public_key=os.environ["LANGFUSE_PUBLIC_KEY"],
    secret_key=os.environ["LANGFUSE_SECRET_KEY"],
    host=os.environ.get("LANGFUSE_HOST", "https://cloud.langfuse.com"),
)
anthropic_client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])


def run_agent_with_tracing(user_query: str):
    """에이전트 실행 전체를 하나의 trace로 기록."""

    # Trace 시작 (사용자 요청 단위)
    trace = lf.trace(
        name="agent-run",
        input=user_query,
        tags=["manual-tracing", "agent"],
        metadata={"user_id": "researcher-01"},
    )

    # --- Span 1: 의도 파악 ---
    intent_span = trace.span(name="intent-classification", input=user_query)
    start = time.time()

    intent_msg = anthropic_client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=64,
        messages=[{"role": "user", "content": f"다음 질문의 의도를 한 단어로 분류해줘 (질문/요청/잡담): {user_query}"}],
    )
    intent = intent_msg.content[0].text.strip()

    intent_span.generation(
        name="classify-intent",
        model="claude-haiku-4-5-20251001",
        input=user_query,
        output=intent,
        usage={"input": intent_msg.usage.input_tokens, "output": intent_msg.usage.output_tokens},
        latency=time.time() - start,
    )
    intent_span.end(output=intent)

    # --- Span 2: 응답 생성 ---
    gen_span = trace.span(name="response-generation", input={"query": user_query, "intent": intent})
    start = time.time()

    response_msg = anthropic_client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        messages=[{"role": "user", "content": user_query}],
    )
    response = response_msg.content[0].text

    gen_span.generation(
        name="generate-response",
        model="claude-sonnet-4-6",
        input=user_query,
        output=response,
        usage={"input": response_msg.usage.input_tokens, "output": response_msg.usage.output_tokens},
        latency=time.time() - start,
    )
    gen_span.end(output=response[:100])

    # Trace 완료
    trace.update(output=response)

    # Langfuse에 flush (비동기 전송 강제)
    lf.flush()

    return trace.id, intent, response


if __name__ == "__main__":
    queries = [
        "멀티에이전트 시스템에서 오케스트레이터 패턴이란?",
        "오늘 날씨 어때?",
    ]

    for query in queries:
        console.print(f"\n[bold blue]Q:[/bold blue] {query}")
        trace_id, intent, response = run_agent_with_tracing(query)
        console.print(f"  의도: [yellow]{intent}[/yellow]")
        console.print(f"  응답: {response[:150]}...")
        console.print(f"  Trace: [dim]cloud.langfuse.com/trace/{trace_id}[/dim]")
