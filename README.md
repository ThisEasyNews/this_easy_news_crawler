# This Easy News Crawler

국내 주요 언론사의 RSS 피드를 수집하고, OpenAI GPT를 활용해 뉴스를 자동 요약 및 분석하는 뉴스 크롤링 파이프라인입니다.

## 주요 기능

- **뉴스 수집**: 다양한 언론사의 RSS 피드를 비동기로 수집 (최대 10개 동시 처리)
- **AI 요약**: GPT-4o-mini를 활용한 뉴스 3줄 요약 및 인사이트 추출
- **키워드 분석**: 기사에서 핵심 키워드 추출 및 일별 언급 횟수 집계
- **데일리 브리핑**: 당일 트렌딩 키워드 기반 3분 브리핑 자동 생성
- **REST API**: FastAPI 기반의 배치 작업 API 제공
- **자동 스케줄링**: GitHub Actions를 통한 6시간 주기 자동 실행

## 기술 스택

| 분류 | 기술 |
|------|------|
| API 서버 | FastAPI, Uvicorn |
| ORM | SQLAlchemy 2.0 |
| 데이터베이스 | PostgreSQL (Supabase) |
| AI | OpenAI GPT-4o-mini |
| RSS 파싱 | Feedparser, Newspaper3k |
| HTTP 클라이언트 | HTTPX (비동기) |
| HTML 파싱 | BeautifulSoup4 |
| 스케줄링 | GitHub Actions |

## 프로젝트 구조

```
this_easy_news_crawler/
├── .github/
│   └── workflows/
│       └── batch.yml          # GitHub Actions 스케줄 설정
├── app/
│   ├── main.py                # FastAPI 앱 진입점
│   ├── api/
│   │   └── v1/
│   │       └── batch.py       # 배치 API 엔드포인트
│   ├── core/
│   │   ├── config.py          # 환경 설정
│   │   ├── database.py        # DB 엔진 및 세션
│   │   └── enums.py           # 상태, 카테고리, 미디어 열거형
│   ├── db/
│   │   ├── create_tables.py   # 테이블 생성 스크립트
│   │   └── seed.py            # 초기 데이터 시드
│   ├── models/                # SQLAlchemy ORM 모델
│   │   ├── article.py
│   │   ├── news_summary.py
│   │   ├── news_keyword.py
│   │   ├── keyword_log.py
│   │   ├── briefing_summary.py
│   │   └── batch_log.py
│   ├── services/
│   │   ├── collector.py       # RSS 수집 서비스
│   │   ├── processor.py       # AI 요약 처리 서비스
│   │   └── briefing.py        # 브리핑 생성 서비스
│   └── utils/
│       ├── gpt_client.py      # OpenAI API 클라이언트
│       └── cleaner.py         # 텍스트 정제 유틸리티
├── run_pipeline.py            # 직접 실행 스크립트
└── requirements.txt
```

## 데이터 처리 흐름

```
1. Collect   →  RSS 피드 파싱 → 기사 저장 (중복 URL 제외)
2. Process   →  미요약 기사 → GPT 요약/인사이트/키워드 추출
3. Analyze   →  키워드 집계 → 일별 언급 횟수 업데이트
4. Brief     →  트렌딩 키워드 Top10 → 3분 브리핑 생성
```

## 지원 카테고리

정치 / 경제 / 사회 / 국제 / 스포츠 / 문화 / 연예 / IT·과학

## 설치 및 실행

### 1. 환경 설정

```bash
git clone https://github.com/ThisEasyNews/this_easy_news_crawler.git
cd this_easy_news_crawler

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### 2. 환경 변수

프로젝트 루트에 `.env` 파일 생성:

```env
OPENAI_API_KEY=sk-proj-...
DATABASE_URL=postgresql://user:password@host:5432/dbname
```

### 3. DB 초기화

```bash
python app/db/create_tables.py
python app/db/seed.py
```

### 4. 실행 방법

**FastAPI 서버 실행:**

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**API 호출:**

```bash
# 뉴스 수집
POST http://localhost:8000/api/v1/batch/collect

# AI 요약 처리
POST http://localhost:8000/api/v1/batch/summarize?limit=5

# 데일리 브리핑 생성
POST http://localhost:8000/api/v1/batch/today-briefing
```

**파이프라인 직접 실행:**

```bash
python run_pipeline.py
```

## 자동 스케줄링 (GitHub Actions)

`.github/workflows/batch.yml`에 설정된 크론 스케줄로 자동 실행됩니다.

| UTC | KST | 작업 |
|-----|-----|------|
| 03:00 | 12:00 | 뉴스 수집 + 요약 |
| 09:00 | 18:00 | 뉴스 수집 + 요약 |
| 15:00 | 00:00 | 뉴스 수집 + 요약 |
| 21:00 | 06:00 | 뉴스 수집 + 요약 |

GitHub Repository Secrets에 `OPENAI_API_KEY`와 `DATABASE_URL`을 등록해야 합니다.

## 데이터베이스 모델

| 테이블 | 설명 |
|--------|------|
| `article` | 수집된 원본 기사 |
| `news_summary` | GPT 생성 요약 (일반 요약 / 브리핑) |
| `news_keyword` | 키워드 마스터 |
| `summary_keyword` | 요약-키워드 N:M 매핑 |
| `keyword_log` | 일별 키워드 언급 횟수 |
| `briefing_summary` | 브리핑-소스기사 매핑 |
| `common_group` / `common_detail` | 카테고리, 미디어, RSS 피드 설정 |
| `batch_log` | 배치 실행 이력 |
