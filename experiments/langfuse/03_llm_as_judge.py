"""
Step 3: Langfuse + LLM-as-judge 통합
응답을 생성하고, judge LLM이 평가한 점수를 trace에 자동으로 attach.
Langfuse 대시보드에서 trace별 점수 추이를 확인할 수 있음.
"""

import os
import json
from dotenv import load_dotenv
from langfuse import Langfuse
import anthropic
from rich.console import Console
from rich.table import Table

load_dotenv("../../.env")
console = Console()

lf = Langfuse(
    public_key=os.environ["LANGFUSE_PUBLIC_KEY"],
    secret_key=os.environ["LANGFUSE_SECRET_KEY"],
    host=os.environ.get("LANGFUSE_HOST", "https://cloud.langfuse.com"),
)
client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

JUDGE_RUBRIC = """다음 응답을 평가하고 JSON으로만 답해라.

질문: {question}
응답: {response}

평가 기준 (각 1-5점):
- accuracy: 사실적으로 정확한가?
- completeness: 질문을 충분히 다루는가?
- conciseness: 핵심만 담고 간결한가?
- overall: 종합 점수

JSON 형식:
{{"accuracy": <int>, "completeness": <int>, "conciseness": <int>, "overall": <int>, "reasoning": "<한 문장>"}}"""


def generate_and_evaluate(question: str) -> dict:
    # 1. 응답 생성 + trace 기록
    trace = lf.trace(name="llm-as-judge-demo", input=question, tags=["judge-eval"])

    gen = trace.generation(name="answer-generation", model="claude-sonnet-4-6", input=question)
    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        messages=[{"role": "user", "content": question}],
    )
    answer = msg.content[0].text
    gen.end(
        output=answer,
        usage={"input": msg.usage.input_tokens, "output": msg.usage.output_tokens},
    )

    # 2. LLM-as-judge 평가
    judge_gen = trace.generation(name="judge-evaluation", model="claude-haiku-4-5-20251001")
    judge_prompt = JUDGE_RUBRIC.format(question=question, response=answer)
    judge_msg = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=256,
        messages=[{"role": "user", "content": judge_prompt}],
    )
    scores = json.loads(judge_msg.content[0].text)
    judge_gen.end(output=scores)

    # 3. Langfuse trace에 점수 attach
    for metric, value in scores.items():
        if metric != "reasoning":
            lf.score(
                trace_id=trace.id,
                name=metric,
                value=value / 5.0,  # 0-1 정규화
                comment=scores["reasoning"] if metric == "overall" else None,
            )

    trace.update(output=answer)
    lf.flush()

    return {"trace_id": trace.id, "answer": answer, "scores": scores}


TEST_QUESTIONS = [
    "LLM의 context window 크기가 성능에 미치는 영향은?",
    "벡터 데이터베이스와 전통적인 관계형 DB의 차이점은?",
]

if __name__ == "__main__":
    table = Table(title="LLM-as-Judge 결과", show_header=True)
    table.add_column("질문", max_width=30)
    table.add_column("accuracy", justify="center")
    table.add_column("completeness", justify="center")
    table.add_column("conciseness", justify="center")
    table.add_column("overall", justify="center")
    table.add_column("근거", max_width=40)

    for q in TEST_QUESTIONS:
        console.print(f"\n[dim]평가 중: {q[:40]}...[/dim]")
        result = generate_and_evaluate(q)
        s = result["scores"]
        table.add_row(
            q[:30] + "...",
            str(s["accuracy"]),
            str(s["completeness"]),
            str(s["conciseness"]),
            f"[bold]{s['overall']}[/bold]",
            s["reasoning"][:40],
        )

    console.print(table)
    console.print("\n[dim]→ cloud.langfuse.com 에서 trace별 점수 추이 확인[/dim]")
