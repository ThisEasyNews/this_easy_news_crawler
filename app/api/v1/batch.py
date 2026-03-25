from typing import Annotated
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func
import asyncio

from app.core.database import get_db, SessionLocal  
from app.services.collector import run_all_categories
from app.models.article import Article
from app.services.processor import process_news_summaries

router = APIRouter()

# 의존성 주입 정의
db_dep = Annotated[Session, Depends(get_db)]

# --- [공통 헬퍼 함수] ---
async def run_collection_process():
    """백그라운드에서 실행될 수집 전용 로직"""
    print("🚀 [Batch] 뉴스 수집 작업을 시작합니다...")
    try:
        await run_all_categories()
        print("✅ [Batch] 모든 카테고리 수집 완료.")
    except Exception as e:
        print(f"❌ [Batch] 수집 중 오류 발생: {e}")

async def run_summary_process(limit: int):
    """백그라운드에서 실행될 요약 전용 로직 (독립 세션 사용)"""
    # BackgroundTask는 요청이 끝난 후 실행되므로 독립적인 DB 세션이 필요합니다.
    db = SessionLocal()
    print(f"🚀 [Batch] AI 요약 작업을 시작합니다. (대상: 최대 {limit}건)")
    try:
        await process_news_summaries(db, limit=limit)
        print("✅ [Batch] 요약 작업 완료.")
    except Exception as e:
        print(f"❌ [Batch] 요약 중 오류 발생: {e}")
    finally:
        db.close()

# --- [엔드포인트] ---

@router.post("/collect", summary="뉴스 수집 배치 실행")
async def trigger_collection(background_tasks: BackgroundTasks):
    """
    모든 카테고리의 RSS 피드로부터 뉴스를 비동기로 수집합니다.
    """
    background_tasks.add_task(run_collection_process)
    return {"message": "뉴스 수집 작업이 백그라운드에서 시작되었습니다."}

@router.post("/summarize", summary="AI 요약 배치 실행")
async def trigger_summarization(background_tasks: BackgroundTasks, limit: int = 5):
    """
    DB에 저장된 미요약 뉴스 중 'limit' 건만큼 GPT 요약을 진행합니다.
    """
    background_tasks.add_task(run_summary_process, limit)
    return {"message": f"최대 {limit}건의 뉴스 요약 작업이 백그라운드에서 시작되었습니다."}

@router.get("/stats", summary="수집 데이터 통계 확인")
def get_collection_stats(db: db_dep):
    """현재 DB에 저장된 기사 수 및 매체별 분포를 확인합니다."""
    total_count = db.query(Article).count()
    
    media_stats = db.query(
        Article.media_id, 
        func.count(Article.id).label("count")
    ).group_by(Article.media_id).all()
    
    recent_articles = db.query(Article).order_by(Article.id.desc()).limit(5).all()
    
    return {
        "total_articles": total_count,
        "media_distribution": {row.media_id: row.count for row in media_stats},
        "recent_entries": [
            {
                "id": a.id, 
                "title": a.original_title, 
                "media": a.media_id,
                "category": a.category_id,
                "scraped_at": a.scraped_at
            } for a in recent_articles
        ]
    }

@router.post("/collect-and-summarize", summary="수집 후 즉시 요약 실행")
async def collect_and_summarize(background_tasks: BackgroundTasks):
    """수집이 끝난 직후 요약을 연속으로 실행합니다."""
    async def run_full_batch():
        await run_collection_process()
        await run_summary_process(limit=5)

    background_tasks.add_task(run_full_batch)
    return {"message": "수집 및 요약 연속 작업이 백그라운드에서 시작되었습니다."}