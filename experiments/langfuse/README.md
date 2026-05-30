# Langfuse 핸즈온

Langfuse Cloud로 LLM tracing + LLM-as-judge 평가까지 한 번에 체험.

## 사전 준비

1. [langfuse.com](https://cloud.langfuse.com) 무료 계정 생성
2. Project 생성 → Settings → API Keys에서 키 발급
3. `.env`에 `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY` 입력

## 실험 구성

| 스크립트 | 내용 |
|---------|------|
| `01_basic_tracing.py` | decorator API로 LLM 호출 자동 추적 |
| `02_manual_tracing.py` | 수동으로 span/generation 구조 직접 제어 |
| `03_llm_as_judge.py` | 응답에 LLM-as-judge 점수 자동 attach |

## 실행

```bash
pip install -r requirements.txt
cp ../../.env .env
python 01_basic_tracing.py
# → Langfuse 대시보드에서 trace 확인
python 03_llm_as_judge.py
# → trace에 score 붙은 것 확인
```

## 확인할 것

- Langfuse UI에서 trace → generation → latency/토큰 확인
- Score가 trace에 자동으로 붙는지
- decorator vs manual 방식의 코드 차이
