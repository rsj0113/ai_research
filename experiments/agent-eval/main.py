"""
LLM-as-Judge 기본 실험.
에이전트 응답을 다른 Claude 인스턴스가 평가한다.
"""

import os
import json
from dotenv import load_dotenv
import anthropic
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

load_dotenv("../../.env")

console = Console()
client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

EVAL_RUBRIC = """
다음 기준으로 응답을 1~5점으로 평가해라. JSON으로만 응답해라.

평가 기준:
- accuracy (정확성): 사실적으로 맞는가?
- completeness (완전성): 질문을 충분히 다루는가?
- conciseness (간결성): 불필요한 내용 없이 핵심만 담는가?

형식:
{
  "accuracy": <1-5>,
  "completeness": <1-5>,
  "conciseness": <1-5>,
  "overall": <1-5>,
  "reasoning": "<판단 근거 한 문장>"
}
"""


def generate_response(question: str, model: str = "claude-sonnet-4-6") -> str:
    msg = client.messages.create(
        model=model,
        max_tokens=512,
        messages=[{"role": "user", "content": question}],
    )
    return msg.content[0].text


def evaluate_response(question: str, response: str, model: str = "claude-haiku-4-5-20251001") -> dict:
    prompt = f"""질문: {question}

응답: {response}

{EVAL_RUBRIC}"""
    msg = client.messages.create(
        model=model,
        max_tokens=256,
        messages=[{"role": "user", "content": prompt}],
    )
    return json.loads(msg.content[0].text)


def run_eval(question: str):
    console.print(f"\n[bold blue]Q:[/bold blue] {question}")

    with console.status("응답 생성 중..."):
        response = generate_response(question)
    console.print(Panel(response, title="응답 (claude-sonnet-4-6)", border_style="green"))

    with console.status("평가 중..."):
        scores = evaluate_response(question, response)

    table = Table(title="평가 결과 (claude-haiku-4-5 judge)")
    table.add_column("기준", style="cyan")
    table.add_column("점수", justify="center")
    for key in ["accuracy", "completeness", "conciseness", "overall"]:
        table.add_row(key, f"{scores[key]}/5")
    console.print(table)
    console.print(f"[dim]근거: {scores['reasoning']}[/dim]")


if __name__ == "__main__":
    test_questions = [
        "RAG와 fine-tuning의 차이를 엔지니어링 관점에서 설명해줘.",
        "LLM agent의 hallucination을 줄이는 실용적인 방법 3가지는?",
    ]
    for q in test_questions:
        run_eval(q)
