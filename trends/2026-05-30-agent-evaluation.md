# Agent Evaluation — 프레임워크 & 방법론 정리

> 수집일: 2026-05-30 | 태그: `#agent-eval` `#llm-as-judge` `#deepeval` `#ragas`

## 한줄 요약

2026년 에이전트 평가 = "tracing without evaluation is expensive logging". 자동화된 평가 루프가 프로덕션 필수 요소로 자리잡는 중.

---

## 평가 접근법

### 1. LLM-as-Judge
LLM이 다른 LLM의 출력을 채점. 가장 유연하고 빠르게 도입 가능.

```
[평가 대상 응답]
       ↓
[Judge LLM + Rubric]
       ↓
점수 (1-5) + 판단 근거
```

**장점**: 사람 수준의 판단력, 커스텀 rubric, 빠른 iteration  
**단점**: judge LLM 비용, position bias, self-evaluation bias  
**완화책**: 여러 모델로 앙상블, chain-of-thought 강제, rubric 구체화

### 2. 코드 기반 평가 (결정론적)
- 정규식, JSON schema 검증, 함수 호출 성공 여부
- 빠르고 재현 가능, 단순 task에 적합
- LLM-as-judge 전에 첫 번째 필터로 활용

### 3. 데이터셋 기반 회귀 테스트
- 황금 테스트셋 구축 → 모델/프롬프트 변경 시 자동 비교
- CI/CD 파이프라인에 통합

---

## 주요 프레임워크 비교

### DeepEval
- **적합**: 프로덕션 멀티에이전트, MCP 툴 사용, 멀티모달
- 50+ 내장 메트릭 (G-Eval, Faithfulness, Answer Relevancy, Hallucination 등)
- G-Eval: chain-of-thought 구조화 채점으로 rubric 기반 LLM judge 구현
- pytest 통합 → CI/CD 친화적
- 링크: [deepeval.com/docs](https://deepeval.com/docs/metrics-introduction)

### RAGAS
- **적합**: RAG 파이프라인 특화
- 핵심 메트릭: Faithfulness, Answer Relevance, Context Precision, Context Recall
- 0.2.x부터 멀티턴 대화 지원
- 링크: [atlan.com 프레임워크 비교](https://atlan.com/know/llm-evaluation-frameworks-compared/)

### MLflow (LLM eval 확장)
- DeepEval, RAGAS, Phoenix judge를 MLflow에서 통합 실행 가능
- 실험 추적과 평가를 한 플랫폼에서
- 링크: [MLflow 서드파티 scorer 발표](https://mlflow.org/blog/third-party-scorers/)

### Braintrust
- 상용 (Series B $80M 2026년 초)
- 25+ 내장 scorer, human annotation workflow
- trace → score → iterate 루프에 최적화

---

## 실무 권장 스택 (2026)

```
간단한 자동 평가      → DeepEval (pytest CI)
RAG 파이프라인       → RAGAS + DeepEval 조합
Tracing + 평가 통합  → Langfuse + LLM-as-judge
대규모 팀, annotation → Braintrust 또는 MLflow
```

---

## 주요 메트릭 용어집

| 메트릭 | 의미 | 주로 쓰는 곳 |
|--------|------|------------|
| Faithfulness | 응답이 source에 근거하는가 | RAG |
| Answer Relevance | 질문에 실제로 답하는가 | 범용 |
| Context Precision | 검색된 컨텍스트가 관련 있는가 | RAG |
| Hallucination | 없는 사실을 지어내는가 | 범용 |
| Tool Call Accuracy | 올바른 툴을 올바른 인자로 호출하는가 | Agent |
| Task Completion | 주어진 목표를 달성했는가 | Agent |

---

## 최신 논문

| 논문 | 링크 | 핵심 |
|------|------|------|
| Benchmark Test-Time Scaling of General LLM Agents (2026.02) | [arXiv 2602.18998](https://arxiv.org/abs/2602.18998) | test-time compute scaling 효과 |
| Agent-as-a-Judge (2026) | [arXiv 2508.02994](https://arxiv.org/pdf/2508.02994) | LLM-as-judge → Agent-as-judge로 진화 |
| LLM Benchmark Audit (2026.05) | [arXiv 2605.21404](https://arxiv.org/html/2605.21404) | 벤치마크 투명성 감사 |
| Survey on LLM Agent Evaluation | [arXiv 2503.16416v2](https://arxiv.org/html/2503.16416v2) | 전체 평가 방법론 서베이 |

---

## 공식 자료

| 자료 | 링크 |
|------|------|
| DeepEval LLM-as-judge | [deepeval.com/guides](https://deepeval.com/guides/guides-llm-as-a-judge) |
| DeepEval 메트릭 소개 | [deepeval.com/docs](https://deepeval.com/docs/metrics-introduction) |
| RAGAS vs TruLens vs DeepEval | [atlan.com 비교](https://atlan.com/know/llm-evaluation-frameworks-compared/) |
| Top 7 평가 툴 2026 | [Confident AI](https://www.confident-ai.com/knowledge-base/compare/best-llm-evaluation-tools) |
| MLflow 서드파티 scorer | [MLflow 블로그](https://mlflow.org/blog/third-party-scorers/) |

---

## 다음 액션

- [ ] `experiments/agent-eval/` 실행해서 기본 LLM-as-judge 체험
- [ ] DeepEval 설치 후 G-Eval 메트릭 직접 써보기
- [ ] RAGAS로 RAG 파이프라인 평가 실험 추가
- [ ] Langfuse + agent-eval 연동 (trace에 점수 자동 attach)
