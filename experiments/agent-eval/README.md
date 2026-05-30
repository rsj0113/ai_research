---
title: "Agent Eval — LLM-as-Judge 기본 실험"
date: 2026-05-30
type: experiment
tags: [agent-eval, llm-as-judge, anthropic]
status: ready
related: ["[[trends/2026-05-30-agent-evaluation]]"]
---

# Agent Eval — LLM-as-Judge 기본 실험

에이전트 응답을 다른 LLM이 평가하는 가장 기본적인 패턴.

## 실행

```bash
pip install -r requirements.txt
cp ../../.env.example ../../.env  # ANTHROPIC_API_KEY 입력
python main.py
```

## 무엇을 실험하는가

1. **응답 생성**: Claude가 질문에 답변
2. **LLM-as-judge 평가**: 다른 Claude 인스턴스가 답변을 scoring
3. **결과 출력**: 점수 + 판단 근거

## 확장 방향

- `--provider openai` 옵션으로 다른 모델 응답과 비교
- Langfuse 연동해서 trace 저장
- 평가 기준(rubric) 커스터마이징
