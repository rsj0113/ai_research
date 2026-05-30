---
title: "AWS Bedrock Guardrails — 공부 자료 정리"
date: 2026-05-30
type: trend
tags: [bedrock, guardrails, safety, aws, pii]
source: [공홈, AWS docs]
related: ["[[experiments/bedrock-guardrails/README]]"]
---

# AWS Bedrock Guardrails — 공부 자료 정리

> 수집일: 2026-05-30 | 태그: `#guardrails` `#bedrock` `#safety`

## 한줄 요약

Bedrock Guardrails = LLM 앞뒤에 붙이는 안전 레이어. 모델 교체 없이 콘텐츠 필터링, PII 마스킹, 환각 감지를 한 번에.

---

## 핵심 기능 5가지

### 1. Content Filters (콘텐츠 필터)
- 카테고리: Hate, Insults, Sexual, Violence, Misconduct, Prompt Attack
- 각 카테고리별 강도(NONE/LOW/MEDIUM/HIGH) 독립 설정
- Standard 티어: 코드 내부(주석, 변수명, 문자열)까지 필터링
- **실무 활용**: 챗봇의 욕설/혐오 발언 차단

### 2. Denied Topics (차단 주제)
- 자연어로 정의: "투자 조언을 제공하는 내용"
- 예시 문장 몇 개만 넣으면 ML이 패턴 학습
- **실무 활용**: 금융 앱에서 투자 추천 질문 차단, 법적 책임 회피

### 3. Sensitive Information Filters (PII 감지/마스킹)
- 내장 PII 타입: SSN, 생년월일, 주소, 신용카드번호, 이메일, 전화번호 등
- Custom regex 추가 가능 (사내 사번, 계좌번호 패턴 등)
- 액션: BLOCK(차단) 또는 ANONYMIZE(마스킹, e.g. `[이름]`)
- **실무 활용**: 고객 개인정보가 LLM 응답에 노출되지 않도록

### 4. Contextual Grounding (환각 감지)
- RAG 응답이 검색된 source에 근거하는지 검사
- Grounding score + Relevance score 반환 (0~1)
- threshold 설정으로 기준 미달 응답 자동 차단
- **실무 활용**: RAG 챗봇에서 근거 없는 답변 필터링

### 5. ApplyGuardrail API (독립 실행)
- LLM 호출 없이 텍스트만 평가 가능
- 기존 파이프라인에 가드레일만 끼워넣을 때 유용
- source: `INPUT`(사용자 입력) / `OUTPUT`(모델 출력) 구분

---

## 아키텍처 패턴

```
사용자 입력
    ↓
[Guardrail - INPUT 검사]  ← PII, 프롬프트 인젝션, 차단 주제
    ↓
LLM (Bedrock 모델)
    ↓
[Guardrail - OUTPUT 검사] ← 환각, PII 마스킹, 콘텐츠 필터
    ↓
사용자 응답
```

---

## 공식 자료

| 자료 | 링크 |
|------|------|
| 공식 문서 | [Bedrock Guardrails Overview](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html) |
| Guardrail 생성 | [Create your guardrail](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-components.html) |
| PII 필터 | [Sensitive information filters](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-sensitive-filters.html) |
| ApplyGuardrail API | [Independent API usage](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-use-independent-api.html) |
| boto3 create_guardrail | [API Reference](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock/client/create_guardrail.html) |
| boto3 apply_guardrail | [API Reference](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-runtime/client/apply_guardrail.html) |
| AWS 공식 샘플 | [amazon-bedrock-samples](https://github.com/aws-samples/amazon-bedrock-samples/blob/main/responsible_ai/bedrock-guardrails/) |

---

## 알아두면 좋은 것

- Guardrail은 **모델에 종속되지 않음** — Claude, Titan, Llama 등 어떤 Bedrock 모델에도 동일하게 적용
- 요금: 텍스트 1K 토큰당 과금 (필터 종류별 상이), Contextual Grounding은 별도 요금
- Streaming 지원: `ConverseStream` API에서도 guardrail 적용 가능
- CloudFormation으로 IaC 관리 가능

---

## 다음 액션

- [ ] `experiments/bedrock-guardrails/` 실험 실행해보기
- [ ] PII 마스킹 + Contextual Grounding 조합 테스트
- [ ] 프로덕션 파이프라인에 ApplyGuardrail API 패턴 적용 검토
