from typing import Annotated
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func
import asyncio

from app.core.database import get_db
from app.services.collector import run_all_categories  # 비동기 전체 수집 함수
from app.models.article import Article

router = APIRouter()

# 의존성 주입 정의
db_dep = Annotated[Session, Depends(get_db)]

def run_async_task(coro):
    """비동기 함수를 동기 백그라운드 태스크에서 실행하기 위한 헬퍼"""
    asyncio.run(coro)

@router.post("/collect", summary="뉴스 카테고리별 비동기 수집 시작")
async def trigger_collection(
    background_tasks: BackgroundTasks
):
    """
    모든 카테고리의 RSS 피드로부터 뉴스를 비동기로 수집합니다.
    (수집량이 많으므로 BackgroundTasks를 통해 실행합니다.)
    """
    # 비동기 함수인 run_all_categories를 백그라운드에서 실행
    background_tasks.add_task(run_async_task, run_all_categories())
    
    return {"message": "카테고리별 뉴스 비동기 수집 작업이 백그라운드에서 시작되었습니다."}

@router.get("/stats", summary="수집 데이터 통계 확인")
def get_collection_stats(db: db_dep):
    # 1. 전체 기사 수 (ID -> id)
    total_count = db.query(Article).count()
    
    # 2. 언론사(media_id)별 기사 수 (대문자 필드들을 소문자로 변경)
    media_stats = db.query(
        Article.media_id, 
        func.count(Article.id).label("count")
    ).group_by(Article.media_id).all()
    
    # 3. 최근 수집된 기사 5개 (ID -> id)
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