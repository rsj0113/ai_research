# AI Research Hub

AI 엔지니어링팀 리서치 허브. 트렌드 모니터링 + 핸즈온 실험을 체계적으로 관리.

## 구조

```
ai_research/
├── trends/          # 트렌드 정리 (자동 수집 + 온디맨드 딥다이브)
└── experiments/     # 핸즈온 실험 코드
```

## 사용법

**온디맨드 딥다이브**
> "Langfuse 최신 동향 정리해줘" → Claude가 검색해서 trends/ 에 추가

**주간 자동 수집**
> 매주 월요일 자동으로 주요 소스에서 트렌드 수집

**실험 실행**
```bash
cp .env.example .env   # API 키 입력
cd experiments/<topic>
python main.py
```

## 다루는 주제

- Agent Evaluation & Benchmarking
- LLM Observability (Langfuse, Braintrust, MLflow)
- Bedrock Guardrails & Safety
- Model Playground & Comparison
- RAG / Memory Architectures
