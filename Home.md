---
title: AI Research Hub
type: home
tags: [home]
---

# AI Research Hub

> AI 엔지니어링팀 리서치 허브 — 트렌드 모니터링 + 핸즈온 실험

---

## 최근 트렌드

```dataview
TABLE date, tags
FROM "trends"
WHERE type = "trend"
SORT date DESC
LIMIT 10
```

---

## 실험 현황

```dataview
TABLE status, tags
FROM "experiments"
WHERE type = "experiment"
SORT date DESC
```

---

## 태그별 보기

```dataview
TABLE date, title
FROM "trends"
WHERE contains(tags, "bedrock") OR contains(tags, "guardrails")
SORT date DESC
```

```dataview
TABLE date, title
FROM "trends"
WHERE contains(tags, "observability") OR contains(tags, "langfuse")
SORT date DESC
```

```dataview
TABLE date, title
FROM "trends"
WHERE contains(tags, "agent-eval") OR contains(tags, "benchmark")
SORT date DESC
```

---

## 빠른 링크

### 트렌드
- [[trends/2026-05-30-latest-digest|📰 최신 동향 (2026-05-30)]]
- [[trends/2026-05-30-bedrock-guardrails|🛡️ Bedrock Guardrails]]
- [[trends/2026-05-30-langfuse|🔭 Langfuse Observability]]
- [[trends/2026-05-30-agent-evaluation|⚖️ Agent Evaluation]]
- [[trends/2026-05-30-agent-observability-evaluation|📊 Agent Obs & Eval 동향]]

### 실험
- [[experiments/agent-eval/README|🧪 Agent Eval (LLM-as-Judge)]]
- [[experiments/langfuse/README|🔭 Langfuse 핸즈온]]
- [[experiments/bedrock-guardrails/README|🛡️ Bedrock Guardrails 핸즈온]]

---

## 주간 수집 현황

매주 월요일 09:00 KST에 자동으로 `trends/YYYY-MM-DD-weekly-digest.md` 생성됨.

---

## 스택

| 프로바이더 | 용도 |
|-----------|------|
| Anthropic Claude API | 실험 기본, LLM-as-judge |
| AWS Bedrock | Guardrails, 엔터프라이즈 모델 |
| OpenAI / Azure | 비교 실험 |
| Ollama / vLLM | 로컬 오픈소스 모델 |
| Langfuse | Observability, 평가 |
