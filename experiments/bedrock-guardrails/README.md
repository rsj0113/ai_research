---
title: "Bedrock Guardrails 핸즈온"
date: 2026-05-30
type: experiment
tags: [bedrock, guardrails, aws, safety, pii]
status: ready
related: ["[[trends/2026-05-30-bedrock-guardrails]]"]
---

# Bedrock Guardrails 핸즈온

Bedrock Guardrails의 핵심 기능을 직접 실험. 가드레일 생성부터 실제 필터링까지.

## 실험 구성

| 스크립트 | 내용 |
|---------|------|
| `01_create_guardrail.py` | 가드레일 생성 (콘텐츠 필터 + PII + 차단 주제) |
| `02_apply_guardrail.py` | ApplyGuardrail API — LLM 없이 텍스트만 평가 |
| `03_converse_with_guardrail.py` | Claude 모델 호출 + 가드레일 동시 적용 |

## 실행

```bash
pip install -r requirements.txt
cp ../../.env .env  # ANTHROPIC_API_KEY, AWS 키 필요
python 01_create_guardrail.py   # guardrail ID 출력됨
python 02_apply_guardrail.py    # 텍스트 평가 테스트
python 03_converse_with_guardrail.py
```

## 확인할 것

- PII(이메일, SSN 등)가 마스킹되는지
- 차단 주제 관련 질문이 막히는지
- 가드레일 action: `BLOCKED` vs `NONE` 차이
- `outputScope: FULL`로 비검출 항목까지 확인하는 법
