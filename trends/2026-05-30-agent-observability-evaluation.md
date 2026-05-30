# Agent Observability & Evaluation — 2026 동향

> 수집일: 2026-05-30 | 태그: `#observability` `#agent-eval` `#benchmark`

## 핵심 요약

2026년 AI 엔지니어링의 화두는 **"tracing without evaluation is expensive logging"**. 에이전트가 무엇을 했는지 보는 것(observability)에서 그게 맞았는지 판단(evaluation)까지 통합하는 방향으로 빠르게 이동 중.

---

## 주요 툴 동향

### Langfuse
- ClickHouse 네이티브 self-hosting 지원으로 데이터 주권 이슈 해결
- 오픈소스 진영에서 가장 빠르게 성장 중
- 실험 우선순위: **높음**

### Braintrust
- 2026년 초 Series B $80M 유치
- 25+ built-in scorer 제공 (NLP, LLM-as-judge, custom)
- 핵심 철학: trace → score → iterate 루프를 빠르게
- [공식 가이드](https://www.braintrust.dev/articles/agent-observability-complete-guide-2026)

### MLflow (LLM 추가)
- Top 5 agent observability tool에 포함됨
- OSS 친화적, 이미 ML 파이프라인 쓰는 팀에 적합
- [MLflow 비교글](https://mlflow.org/top-5-agent-observability-tools/)

---

## 주요 논문

### Benchmark Test-Time Scaling of General LLM Agents (2026.02)
- arXiv: [2602.18998](https://arxiv.org/abs/2602.18998)
- 핵심: LLM agent의 test-time compute scaling 효과 측정
- **읽을 이유**: 에이전트에 더 많은 compute를 주면 얼마나 좋아지는지 benchmark

### What Twelve LLM Agent Benchmark Papers Disclose About Themselves (2026.05)
- arXiv: [2605.21404](https://arxiv.org/html/2605.21404)
- 핵심: 기존 벤치마크 논문들의 재현성/투명성 감사 (pilot audit)
- **읽을 이유**: 벤치마크 믿기 전에 어떤 함정이 있는지 파악

### A Survey on Evaluation of LLM-based Agents (2025.03, v2 2026)
- arXiv: [2503.16416v2](https://arxiv.org/html/2503.16416v2)
- 핵심: agent evaluation 전체 survey, 최신 업데이트됨
- **읽을 이유**: 팀 내 평가 기준 잡기 전 필독

---

## 주목할 벤치마크

| 벤치마크 | 특징 |
|---------|------|
| **AgencyBench** | 1M 토큰 실세계 컨텍스트에서 자율 에이전트 평가 |
| **MASEval** | 멀티에이전트 시스템 단위 평가 (모델→시스템으로 확장) |
| **MCP Atlas** (Scale) | MCP 기반 툴 사용 에이전트 평가 |
| **Tool-Decathlon** | 다양한 툴 사용 능력 종합 평가 |

---

## 업계 수치

- Gartner 예측: 2028년까지 60% 소프트웨어 팀이 AI 평가/observability 플랫폼 도입 (2025년 18% → 3배 성장)

---

## 다음 액션

- [ ] Langfuse self-hosting 실험 → `experiments/observability/langfuse/`
- [ ] Braintrust scorer 직접 써보기
- [ ] `2503.16416v2` survey 읽고 팀 평가 기준 초안 작성
