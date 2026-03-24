# 배치 작업 수동 트리거 및 상태 확인 API
from typing import Annotated
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.collector import collect_news_task
from app.models.article import Article
from sqlalchemy import func

router = APIRouter()

db_dep = Annotated[Session, Depends(get_db)]

@router.post("/collect", summary="뉴스 수집 시작")
def trigger_collection(
    background_tasks: BackgroundTasks, 
    db: db_dep
):
    """
    RSS 피드로부터 뉴스를 수집하여 ARTICLE 테이블에 저장합니다.
    (수집량이 많을 수 있으므로 백그라운드 작업으로 실행합니다.)
    """
    # 즉시 응답을 주고 수집은 백그라운드에서 진행 (Swagger 타임아웃 방지)
    background_tasks.add_task(collect_news_task, db)
    
    return {"message": "뉴스 수집 작업이 백그라운드에서 시작되었습니다."}

@router.get("/stats", summary="수집 데이터 통계 확인")
def get_collection_stats(db: db_dep):
    # 1. 전체 기사 수
    total_count = db.query(Article).count()
    
    # 2. 언론사(MEDIA_ID)별 기사 수
    media_stats = db.query(
        Article.MEDIA_ID, 
        func.count(Article.ID).label("count")
    ).group_by(Article.MEDIA_ID).all()
    
    # 3. 최근 수집된 기사 5개 요약
    recent_articles = db.query(Article).order_by(Article.ID.desc()).limit(5).all()
    
    return {
        "total_articles": total_count,
        "media_distribution": {row.MEDIA_ID: row.count for row in media_stats},
        "recent_entries": [
            {
                "id": a.ID, 
                "title": a.ORIGINAL_TITLE, 
                "media": a.MEDIA_ID,
                "scraped_at": a.SCRAPED_AT
            } for a in recent_articles
        ]
    }