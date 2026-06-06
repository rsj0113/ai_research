# CLAUDE.md

이 파일은 Claude Code(claude.ai/code)가 이 저장소에서 작업할 때 참고하는 안내 문서입니다.

## 프로젝트 개요

이 저장소는 **AI Research Hub** — 트렌드 모니터링과 실습 실험을 결합한 개인 연구 공간입니다. 두 개의 작업 영역으로 구성됩니다:

- `trends/` — Claude가 수집한 Markdown 리서치 노트 (자동 수집 및 온디맨드)
- `experiments/` — 독립적으로 실행 가능한 Python 실험 폴더 모음

저장소는 [Obsidian](https://obsidian.md) 지식 베이스로도 활용되며, `Home.md`가 대시보드 역할을 하며 Dataview 쿼리로 최신 트렌드와 실험 현황을 표시합니다.

## 환경 설정

모든 시크릿은 `.env`에 저장합니다(커밋 제외). `.env.example`을 복사한 뒤 실행할 실험에 필요한 키를 채워 넣습니다:

```bash
cp .env.example .env
```

영역별 필수 키:
- **Anthropic 실험**: `ANTHROPIC_API_KEY`
- **OpenAI / Azure 실험**: `OPENAI_API_KEY` (Azure 사용 시 추가 키 필요)
- **Bedrock 실험**: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_DEFAULT_REGION`
- **Langfuse 트레이싱**: `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_HOST`
- **AI 다이제스트 스크립트**: `SLACK_WEBHOOK_URL`, `TWITTER_BEARER_TOKEN` (선택)

## 실험 실행

각 실험 폴더는 독립적인 `requirements.txt`를 가집니다. 기본 실행 패턴:

```bash
cd experiments/<topic>
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python main.py          # 또는 번호 스크립트: python 01_create_guardrail.py
```

### Bedrock Guardrails (순서대로 실행 필수)

```bash
cd experiments/bedrock-guardrails
python 01_create_guardrail.py          # 가드레일 생성 → guardrailId/version 출력 후 .env에 기록
python 02_apply_guardrail.py           # LLM 호출 없이 가드레일 단독 테스트
python 03_converse_with_guardrail.py   # 가드레일 적용 상태에서 Claude와 실제 대화
```

`01_create_guardrail.py`를 반드시 먼저 실행해야 합니다. 이후 스크립트들이 여기서 생성된 AWS 리소스 ID를 필요로 합니다.

### AI 다이제스트 스크립트

```bash
cd scripts
python ai_digest.py
```

HackerNews(Algolia API), arXiv(XML 피드), YouTube RSS, 선택적으로 Threads/X에서 데이터를 수집합니다. GPT-4o-mini로 제목을 한국어로 번역한 뒤 Slack으로 전송합니다.

## 아키텍처

### 실험 설계 패턴

각 실험 폴더는 번호 스크립트가 단계적으로 쌓이는 구조를 따릅니다 (`01_`은 인프라 생성, `02_`는 독립 적용, `03_`은 LLM 통합). Langfuse(기본 트레이싱 → 수동 트레이싱 → LLM-as-judge)와 Bedrock Guardrails 모두 이 패턴을 공유합니다.

스크립트 내부의 공통 흐름:
1. `python-dotenv`로 환경 변수 로드
2. SDK 클라이언트 초기화 (Anthropic, OpenAI, Boto3, Langfuse)
3. 테스트 케이스 또는 프롬프트 인라인 정의
4. `rich` 라이브러리로 콘솔 출력 (테이블, 패널) → 시각적 검증

### LLM-as-Judge 패턴 (`experiments/agent-eval/`, `experiments/langfuse/03_llm_as_judge.py`)

생성 LLM이 응답을 만들면, 별도의 평가 LLM이 루브릭(정확성, 완성도, 간결성)에 따라 점수를 매깁니다. 점수는 0–1로 정규화되며, Langfuse 활성 시 트레이스에 score로 첨부되어 대시보드에서 확인할 수 있습니다.

### Langfuse 통합

실험 전반에 걸쳐 두 가지 트레이싱 방식이 사용됩니다:
- **데코레이터 방식** (`@observe()`): 함수를 자동으로 감싸 스팬 기록 — `01_basic_tracing.py`에서 사용
- **수동 컨텍스트 매니저** (`start_as_current_observation()`): 스팬/제너레이션 직접 제어 — `02_manual_tracing.py`에서 사용

`langfuse.openai.openai` 클라이언트는 표준 OpenAI 클라이언트의 드롭인 대체재로, 제너레이션을 자동으로 캡처합니다.

### 트렌드 작성 규칙

`trends/` 의 노트는 다음 프론트매터를 사용합니다:

```yaml
---
date: YYYY-MM-DD
tags: [tag1, tag2]
sources: [url1, url2]
---
```

`Home.md`의 Dataview 쿼리는 `date` 기준으로 최신 10개 항목을 표시합니다. 새 트렌드 노트 작성 시 `templates/trend.md`를, 새 실험 노트 작성 시 `templates/experiment.md`를 기반으로 사용합니다.

### 데일리 로그

작업 진행 상황과 다음 단계 메모는 `daily/YYYY-MM-DD.md`에 기록합니다. 형식은 자유롭고 템플릿을 사용하지 않습니다.
