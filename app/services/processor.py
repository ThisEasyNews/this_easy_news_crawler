import json
from datetime import datetime
from openai import AsyncOpenAI
from sqlalchemy.orm import Session
from difflib import SequenceMatcher

from app.core.config import settings
from app.models.article import Article
from app.models.news_summary import NewsSummary
from app.models.news_keyword import NewsKeyword
from app.models.summary_keyword import SummaryKeyword
from app.models.keyword_log import KeywordLog

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

def get_similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

def _get_insight_instruction(category_id: str) -> str:
    """카테고리에 따른 인사이트 가이드라인 생성"""
    target_categories = ['CAT_POLITICS', 'CAT_ECONOMY', 'CAT_TECH_SCIENCE']
    if category_id in target_categories:
        return (
            "3. 인사이트(insight): 이 뉴스가 해당 산업이나 사회 전반에 미칠 핵심 영향을 "
            "전문적인 분석가 톤으로 1문장 작성해줘. 문장은 반드시 '~할 것으로 전망됨', "
            "'~가 예상됨', '~에 기여할 것으로 보임' 등으로 끝나야 해."
        )
    return "3. 인사이트(insight): 이 기사는 인사이트 추출 대상이 아니므로 null로 반환해."

async def _get_gpt_analysis(title: str, content: str, insight_instruction: str):
    """GPT API 호출 및 응답 파싱"""
    prompt = f"""
    아래 뉴스 데이터를 분석해서 JSON 형식으로 응답해줘.
    [데이터] 제목: {title} | 본문: {content[:2000]}
    [응답 요구사항]
    1. 제목(title): 핵심 내용을 반영한 짧은 제목.
    2. 요약(summary): 300자 이내 혹은 유사도 80% 이상시 원문 활용, 그 외 3줄 요약.
    3. 키워드(keywords): 중요 키워드 1~3개 리스트.
    {insight_instruction}
    """
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "너는 뉴스 분석 전문가야. 반드시 JSON 형식으로만 응답해."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].message.content)

def _process_keywords(db: Session, summary_id: int, keywords: list, target_date: datetime):
    """
    1. NewsKeyword: 키워드 자체 관리 (Master)
    2. SummaryKeyword: 요약본-키워드 매핑 (N:M)
    3. KeywordLog: 일별 키워드 언급 횟수 관리 (Statistics)
    """
    # 오늘 날짜만 추출 (시간 제외)
    today = target_date.date()

    for kw_text in keywords:
        kw_text = kw_text.strip()
        if not kw_text: continue
        
        # 1. NewsKeyword 처리 (Master)
        keyword_obj = db.query(NewsKeyword).filter(NewsKeyword.keyword == kw_text).first()
        if not keyword_obj:
            keyword_obj = NewsKeyword(keyword=kw_text)
            db.add(keyword_obj)
            db.flush() # keyword_obj.id 확보
        
        # 2. SummaryKeyword 처리 (N:M 매핑)
        exists_link = db.query(SummaryKeyword).filter_by(
            summary_id=summary_id, 
            keyword_id=keyword_obj.id
        ).first()
        if not exists_link:
            db.add(SummaryKeyword(summary_id=summary_id, keyword_id=keyword_obj.id))

        # 3. KeywordLog 처리 (일별 통계 업데이트)
        # 해당 날짜에 해당 키워드가 이미 있는지 확인
        log_entry = db.query(KeywordLog).filter(
            KeywordLog.keyword_id == keyword_obj.id,
            KeywordLog.target_date == today
        ).first()

        if log_entry:
            # 이미 오늘 기록이 있다면 카운트만 +1 (Update)
            log_entry.mention_count += 1
        else:
            # 오늘 처음 나온 키워드라면 새로 생성 (Insert)
            new_log = KeywordLog(
                keyword_id=keyword_obj.id,
                target_date=today,
                mention_count=1,
                status_code="PUBLISHED"
            )
            db.add(new_log)

async def process_news_summaries(db: Session, limit: int = 100):
    """메인 프로세스: 미요약 뉴스 추출 및 처리"""
    articles = db.query(Article).filter(Article.is_summarized == False).order_by(Article.created_at.desc()).limit(limit).all()
    if not articles:
        print("[*] 요약할 새로운 기사가 없습니다.")
        return

    print(f"🚀 총 {len(articles)}건의 뉴스 요약을 시작합니다. (비동기 모드)")

    for article in articles:
        try:
            content = article.feedparser_content or article.crawler_content
            if not content or len(content.strip()) < 10: continue

            # 1. GPT 분석 요청
            insight_instr = _get_insight_instruction(article.category_id)
            res_data = await _get_gpt_analysis(article.original_title, content, insight_instr)
            
            # 2. 요약본 저장
            new_summary = NewsSummary(
                article_id=article.id,
                title=res_data.get('title') or article.original_title,
                summary_content=res_data.get('summary'),
                insight=res_data.get('insight'),
                ai_model="gpt-4o-mini",
                top_image_url=article.image_url, 
                target_date=article.published_at.date() if article.published_at else datetime.now().date(), 
                created_at=datetime.now()
            )
            
            db.add(new_summary)
            db.flush()

            # 3. 키워드 연결 및 일별 로그 업데이트
            _process_keywords(
                db, 
                new_summary.id, 
                res_data.get('keywords', []), 
                article.published_at # 기사 게시일 기준
            )
            article.is_summarized = True
            db.commit()
            
            similarity = get_similarity(article.original_title, content)
            print(f"  ✅ 요약 완료: {article.original_title[:20]}... (유사도: {similarity:.2f})")

        except Exception as e:
            db.rollback()
            print(f"  ❌ 요약 실패 ({article.id}): {str(e)}")

