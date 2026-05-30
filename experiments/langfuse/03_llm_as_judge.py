"""
Step 3: Langfuse + LLM-as-judge 통합
응답을 생성하고, judge LLM이 평가한 점수를 trace에 자동으로 attach.
Langfuse 대시보드에서 trace별 점수 추이를 확인할 수 있음.
"""

import os
import json
from dotenv import load_dotenv
from langfuse import get_client
from openai import OpenAI
from rich.console import Console
from rich.table import Table

load_dotenv("../../.env")
console = Console()

lf = get_client()
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

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
    with lf.start_as_current_observation(
        name="llm-as-judge-demo",
        as_type="span",
        input=question,
        metadata={"tags": ["judge-eval"]},
    ):
        # 1. 응답 생성
        with lf.start_as_current_observation(name="answer-generation", as_type="generation"):
            msg = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": question}],
                max_tokens=512,
            )
            answer = msg.choices[0].message.content
            lf.update_current_generation(
                model="gpt-4o",
                input=question,
                output=answer,
                usage_details={
                    "input": msg.usage.prompt_tokens,
                    "output": msg.usage.completion_tokens,
                },
            )

        # 2. LLM-as-judge 평가
        judge_prompt = JUDGE_RUBRIC.format(question=question, response=answer)
        with lf.start_as_current_observation(name="judge-evaluation", as_type="generation"):
            judge_msg = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": judge_prompt}],
                max_tokens=256,
                response_format={"type": "json_object"},
            )
            scores = json.loads(judge_msg.choices[0].message.content)
            lf.update_current_generation(
                model="gpt-4o-mini",
                input=judge_prompt,
                output=scores,
                usage_details={
                    "input": judge_msg.usage.prompt_tokens,
                    "output": judge_msg.usage.completion_tokens,
                },
            )

        # 3. 점수를 trace에 attach
        for metric, value in scores.items():
            if metric != "reasoning":
                lf.score_current_trace(
                    name=metric,
                    value=value / 5.0,  # 0-1 정규화
                    comment=scores["reasoning"] if metric == "overall" else None,
                )

        lf.update_current_span(output={"answer": answer, "scores": scores})

    lf.flush()
    return {"answer": answer, "scores": scores}


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
