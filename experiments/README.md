# Experiments

핸즈온 실험 코드. 각 디렉토리는 독립 실험.

## 실행 방법

```bash
cp ../.env.example ../.env  # 루트에서 한 번만 — API 키 입력
cd <experiment-dir>
pip install -r requirements.txt
python <script>.py
```

## 실험 목록

| 디렉토리 | 주제 | 필요 키 | 상태 |
|---------|------|---------|------|
| `agent-eval/` | LLM-as-judge 기본 패턴 | ANTHROPIC_API_KEY | 완료 |
| `bedrock-guardrails/` | Bedrock Guardrail 생성 + 콘텐츠 필터 + PII | AWS_* | 완료 |
| `langfuse/` | LLM tracing + LLM-as-judge + 점수 attach | ANTHROPIC_API_KEY, LANGFUSE_* | 완료 |

## 순서 추천

처음이라면 이 순서로 실행:

1. **agent-eval/** — API 키 하나로 바로 실행 가능. LLM-as-judge 감각 익히기
2. **langfuse/** — Langfuse 계정 만들고 tracing 체험 (무료)
3. **bedrock-guardrails/** — AWS 계정 + IAM 권한 필요
