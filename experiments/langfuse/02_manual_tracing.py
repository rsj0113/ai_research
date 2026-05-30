"""
Step 2: Langfuse manual tracing — start_as_current_observation으로 span/generation 직접 제어.
decorator로 안 되는 세밀한 제어가 필요할 때 이 방식.
"""

import os
from dotenv import load_dotenv
from langfuse import get_client
from openai import OpenAI
from rich.console import Console

load_dotenv("../../.env")
console = Console()

lf = get_client()
openai_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])


def run_agent_with_tracing(user_query: str):
    """에이전트 실행 전체를 하나의 trace로 기록."""

    with lf.start_as_current_observation(
        name="agent-run",
        as_type="agent",
        input=user_query,
        metadata={"user_id": "researcher-01"},
    ):

        # --- Span 1: 의도 파악 ---
        with lf.start_as_current_observation(name="intent-classification", as_type="span", input=user_query):
            with lf.start_as_current_observation(name="classify-intent", as_type="generation"):
                prompt = f"다음 질문의 의도를 한 단어로 분류해줘 (질문/요청/잡담): {user_query}"
                msg = openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=16,
                )
                intent = msg.choices[0].message.content.strip()
                lf.update_current_generation(
                    model="gpt-4o-mini",
                    input=prompt,
                    output=intent,
                    usage_details={
                        "input": msg.usage.prompt_tokens,
                        "output": msg.usage.completion_tokens,
                    },
                )

        # --- Span 2: 응답 생성 ---
        with lf.start_as_current_observation(
            name="response-generation",
            as_type="span",
            input={"query": user_query, "intent": intent},
        ):
            with lf.start_as_current_observation(name="generate-response", as_type="generation"):
                msg = openai_client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": user_query}],
                    max_tokens=512,
                )
                response = msg.choices[0].message.content
                lf.update_current_generation(
                    model="gpt-4o",
                    input=user_query,
                    output=response,
                    usage_details={
                        "input": msg.usage.prompt_tokens,
                        "output": msg.usage.completion_tokens,
                    },
                )

        trace_id = lf.get_current_trace_id()
        lf.update_current_span(output=response)

    lf.flush()
    return trace_id, intent, response


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
        console.print(f"  Trace ID: [dim]{trace_id}[/dim]")
