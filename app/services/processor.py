import asyncio
import time
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
from app.utils.gpt_client import get_gpt_analysis, get_insight_instruction

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

def get_similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

def _process_keywords(db: Session, summary_id: int, keywords: list, target_date: datetime):
    base_date = target_date if target_date else datetime.now()
    today = base_date.date()

    for kw_text in keywords:
        kw_text = kw_text.strip()
        if not kw_text:
            continue

        keyword_obj = db.query(NewsKeyword).filter(NewsKeyword.keyword == kw_text).first()
        if not keyword_obj:
            keyword_obj = NewsKeyword(keyword=kw_text)
            db.add(keyword_obj)
            db.flush()

        exists_link = db.query(SummaryKeyword).filter_by(
            summary_id=summary_id,
            keyword_id=keyword_obj.id
        ).first()
        if not exists_link:
            db.add(SummaryKeyword(summary_id=summary_id, keyword_id=keyword_obj.id))

        log_entry = db.query(KeywordLog).filter(
            KeywordLog.keyword_id == keyword_obj.id,
            KeywordLog.target_date == today
        ).first()

        if log_entry:
            log_entry.mention_count += 1
        else:
            db.add(KeywordLog(
                keyword_id=keyword_obj.id,
                target_date=today,
                mention_count=1,
                status_code="PUBLISHED"
            ))


async def _analyze_single_article(article: Article):
    """GPT 분석만 수행 (DB 조작 없음). 성공 시 (article, res_data) 반환."""
    try:
        content = article.feedparser_content or article.crawler_content
        if not content or len(content.strip()) < 10:
            return None

        insight_instr = get_insight_instruction(category_id=article.category_id)
        res_data = await get_gpt_analysis(article.original_title, content, insight_instr)

        if not res_data.get('summary'):
            raise ValueError(f"GPT 요약 내용 없음 (Article ID: {article.id})")

        return (article, res_data)

    except Exception as e:
        print(f"  ❌ GPT 분석 실패 ({article.id}): {str(e)}")
        return None


async def process_category_batch(db: Session, c_id: str, limit: int):
    """카테고리 내 기사를 병렬 GPT 분석 후 결과 반환 (DB 저장 없음)"""
    await asyncio.sleep(0.5)
    cat_start = time.time()

    category_articles = db.query(Article).filter(
        Article.is_summarized == False,
        Article.category_id == c_id
    ).order_by(Article.created_at.desc()).limit(limit).all()

    if not category_articles:
        return [], 0

    print(f"📂 [카테고리 ID: {c_id}] {len(category_articles)}건 GPT 분석 시작...")

    tasks = [_analyze_single_article(article) for article in category_articles]
    raw_results = await asyncio.gather(*tasks)

    valid_results = [r for r in raw_results if r is not None]
    print(f"⏱️ {c_id} 완료: {time.time() - cat_start:.2f}초 (성공: {len(valid_results)}/{len(category_articles)})")

    return valid_results, len(category_articles)


def _bulk_save(db: Session, analysis_results: list):
    """분석 결과 전체를 한 번에 DB 저장 후 단일 커밋"""
    if not analysis_results:
        return 0

    # 1. NewsSummary 전체 추가 후 flush로 ID 한 번에 확보
    summary_mappings = []
    for article, res_data in analysis_results:
        new_summary = NewsSummary(
            title=res_data.get('title') or article.original_title,
            summary_content=res_data.get('summary'),
            insight=res_data.get('insight'),
            ai_model="gpt-4o-mini",
            top_image_url=article.image_url,
            target_date=article.published_at.date() if article.published_at else datetime.now().date(),
            created_at=datetime.now()
        )
        db.add(new_summary)
        summary_mappings.append((article, res_data, new_summary))

    db.flush()

    # 2. Article 업데이트 + 키워드 처리 (커밋 없이)
    for article, res_data, new_summary in summary_mappings:
        article.summary_id = new_summary.id
        article.is_summarized = True
        _process_keywords(db, new_summary.id, res_data.get('keywords', []), article.published_at)

    # 3. 단일 커밋
    db.commit()
    print(f"💾 {len(analysis_results)}건 일괄 저장 완료")
    return len(analysis_results)


async def process_news_summaries(db: Session, limit: int = 20):
    """메인 프로세스: 전 카테고리 병렬 GPT 분석 → 한 번에 저장"""
    categories = db.query(Article.category_id).filter(
        Article.is_summarized == False
    ).distinct().all()

    category_ids = [c[0] for c in categories if c[0] is not None]

    if not category_ids:
        print("[*] 요약할 새로운 기사가 없습니다.")
        return 0

    print(f"🚀 총 {len(category_ids)}개 카테고리 동시 GPT 분석 시작...")
    total_start = time.time()

    cat_tasks = [process_category_batch(db, c_id, limit) for c_id in category_ids]
    cat_results = await asyncio.gather(*cat_tasks)

    all_valid = [item for results, _ in cat_results for item in results]
    total_attempted = sum(count for _, count in cat_results)

    print(f"\n🤖 GPT 분석 완료: {time.time() - total_start:.2f}초 | 성공: {len(all_valid)}/{total_attempted}건")

    try:
        _bulk_save(db, all_valid)
    except Exception as e:
        db.rollback()
        print(f"❌ 일괄 저장 실패: {str(e)}")
        return 0

    print(f"✨ 전체 완료. 총 소요 시간: {time.time() - total_start:.2f}초")
    return total_attempted
