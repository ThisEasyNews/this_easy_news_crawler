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
    """
    1. NewsKeyword: 키워드 자체 관리 (Master)
    2. SummaryKeyword: 요약본-키워드 매핑 (N:M)
    3. KeywordLog: 일별 키워드 언급 횟수 관리 (Statistics)
    """
    # 날짜 정보가 없을 경우 현재 시간 기준 처리
    base_date = target_date if target_date else datetime.now()
    today = base_date.date()

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
        log_entry = db.query(KeywordLog).filter(
            KeywordLog.keyword_id == keyword_obj.id,
            KeywordLog.target_date == today
        ).first()

        if log_entry:
            log_entry.mention_count += 1
        else:
            new_log = KeywordLog(
                keyword_id=keyword_obj.id,
                target_date=today,
                mention_count=1,
                status_code="PUBLISHED"
            )
            db.add(new_log)

async def process_single_article(db: Session, article: Article):
    """기사 한 개를 처리하는 최소 단위 비동기 함수 (기존과 동일)"""
    try:
        content = article.feedparser_content or article.crawler_content
        if not content or len(content.strip()) < 10: 
            return False

        # 1. GPT 분석 요청
        insight_instr = get_insight_instruction(category_id=article.category_id)
        res_data = await get_gpt_analysis(article.original_title, content, insight_instr)
        
        summary_text = res_data.get('summary')
        if not summary_text:
            raise ValueError(f"GPT로부터 요약 내용을 받지 못했습니다. (Article ID: {article.id})")
        
        # 2. 요약본 저장
        new_summary = NewsSummary(
            title=res_data.get('title') or article.original_title,
            summary_content=summary_text,
            insight=res_data.get('insight'),
            ai_model="gpt-4o-mini",
            top_image_url=article.image_url, 
            target_date=article.published_at.date() if article.published_at else datetime.now().date(), 
            created_at=datetime.now()
        )
        
        db.add(new_summary)
        db.flush() 

        # 3. 기사 업데이트
        article.summary_id = new_summary.id
        article.is_summarized = True

        # 4. 키워드 처리
        _process_keywords(db, new_summary.id, res_data.get('keywords', []), article.published_at)
        
        db.commit()
        return True

    except Exception as e:
        db.rollback()
        print(f"  ❌ 요약 실패 ({article.id}): {str(e)}")
        return False

async def process_category_batch(db: Session, c_id: str, limit: int):
    """
    특정 카테고리 한 개를 처리하고 소요 시간을 측정하는 비동기 단위
    """
    await asyncio.sleep(0.5)
    cat_start_time = time.time()
    
    # 해당 카테고리의 미요약 기사 가져오기
    category_articles = db.query(Article).filter(
        Article.is_summarized == False,
        Article.category_id == c_id
    ).order_by(Article.created_at.desc()).limit(limit).all()

    if not category_articles:
        return 0, 0, 0 # 성공수, 총수, 소요시간

    print(f"📂 [카테고리 ID: {c_id}] {len(category_articles)}건 처리 시작...")

    # 카테고리 내 기사들 병렬 처리
    tasks = [process_single_article(db, article) for article in category_articles]
    results = await asyncio.gather(*tasks)
    
    cat_end_time = time.time()
    duration = cat_end_time - cat_start_time
    success_count = sum(1 for r in results if r is True)
    
    print(f"⏱️ 카테고리 {c_id} 완료! 소요 시간: {duration:.2f}초 (성공: {success_count}/{len(category_articles)})")
    
    return success_count, len(category_articles), duration


async def process_news_summaries(db: Session, limit: int = 5):
    """
    메인 프로세스: 모든 카테고리를 동시에 시작 (완전 비동기)
    """
    # 1. 미요약 기사가 있는 카테고리 ID 목록 추출
    categories = db.query(Article.category_id).filter(
        Article.is_summarized == False
    ).distinct().all()

    category_ids = [c[0] for c in categories if c[0] is not None]

    if not category_ids:
        print("[*] 요약할 새로운 기사가 없습니다.")
        return

    print(f"🚀 총 {len(category_ids)}개 카테고리를 동시에 요약 시작합니다.")
    total_start_time = time.time()

    # 2. 모든 카테고리 작업을 태스크로 생성하여 동시에 실행
    cat_tasks = [process_category_batch(db, c_id, limit) for c_id in category_ids]
    
    # [핵심] 여기서 모든 카테고리가 동시에 발사됩니다.
    await asyncio.gather(*cat_tasks)

    total_end_time = time.time()
    print(f"\n✨ 모든 작업 완료. 실제 병렬 소요 시간: {total_end_time - total_start_time:.2f}초")


# async def process_news_summaries(db: Session, limit: int = 100):
#     """메인 프로세스: 미요약 뉴스 추출 및 처리 (변경된 DB 구조 반영)"""
#     articles = db.query(Article).filter(Article.is_summarized == False).order_by(Article.created_at.desc()).limit(limit).all()
    
#     if not articles:
#         print("[*] 요약할 새로운 기사가 없습니다.")
#         return

#     print(f"🚀 총 {len(articles)}건의 뉴스 요약을 시작합니다. (비동기 모드)")

#     for article in articles:
#         try:
#             content = article.feedparser_content or article.crawler_content
#             if not content or len(content.strip()) < 10: 
#                 continue

#             # 1. GPT 분석 요청 (공통 함수 사용)
#             insight_instr = get_insight_instruction(category_id=article.category_id)
#             res_data = await get_gpt_analysis(article.original_title, content, insight_instr)
            
#             # 2. 요약본 저장 (이제 article_id를 저장하지 않고 독립적으로 생성)
#             new_summary = NewsSummary(
#                 title=res_data.get('title') or article.original_title,
#                 summary_content=res_data.get('summary'),
#                 insight=res_data.get('insight'),
#                 ai_model="gpt-4o-mini",
#                 top_image_url=article.image_url, 
#                 target_date=article.published_at.date() if article.published_at else datetime.now().date(), 
#                 created_at=datetime.now()
#             )
            
#             db.add(new_summary)
#             db.flush() # new_summary.id 확보

#             # 3. 기사(Article)에 요약 정보 업데이트 (관계 역전 반영)
#             article.summary_id = new_summary.id
#             article.is_summarized = True

#             # 4. 키워드 연결 및 일별 로그 업데이트
#             _process_keywords(
#                 db, 
#                 new_summary.id, 
#                 res_data.get('keywords', []), 
#                 article.published_at # 기사 게시일 기준
#             )
            
#             db.commit()
            
#             similarity = get_similarity(article.original_title, content)
#             print(f"  ✅ 요약 완료: {article.original_title[:20]}... (유사도: {similarity:.2f})")

#         except Exception as e:
#             db.rollback()
#             print(f"  ❌ 요약 실패 ({article.id}): {str(e)}")