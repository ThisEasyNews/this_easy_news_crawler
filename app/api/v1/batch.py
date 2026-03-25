from typing import Annotated
from pydantic import BaseModel
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
import asyncio

from app.core.database import get_db, SessionLocal  
from app.services.briefing import create_daily_briefing
from app.services.collector import run_all_categories
from app.models.article import Article
from app.services.processor import process_news_summaries

router = APIRouter()

# 의존성 주입 정의
db_dep = Annotated[Session, Depends(get_db)]

class BatchResponse(BaseModel):
    status: str
    message: str
    detail: str
    
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

@router.post("/collect", summary="뉴스 수집 배치 실행",
    responses={
        200: {"description": "백그라운드 수집 시작 성공"},
        500: {"description": "작업 스케줄링 실패"}
        }
    )
async def trigger_collection(background_tasks: BackgroundTasks):
    """
    모든 카테고리의 RSS 피드로부터 뉴스를 비동기로 수집합니다.
    """
    try:
        background_tasks.add_task(run_collection_process)
        return {"message": "뉴스 수집 작업이 백그라운드에서 시작되었습니다."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"수집 작업 등록 실패: {str(e)}")


@router.post("/summarize", summary="AI 요약 배치 실행",
    responses={
        200: {"description": "백그라운드 요약 시작 성공"},
        500: {"description": "작업 스케줄링 실패"}
        }
    )
async def trigger_summarization(background_tasks: BackgroundTasks, limit: int = 5):
    """
    DB에 저장된 미요약 뉴스 중 'limit' 건만큼 GPT 요약을 진행합니다.
    """
    try:
        background_tasks.add_task(run_summary_process, limit)
        return {"message": f"최대 {limit}건의 뉴스 요약 작업이 백그라운드에서 시작되었습니다."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"요약 작업 등록 실패: {str(e)}")


@router.get("/stats", summary="수집 데이터 통계 확인",
            responses={
        200: {"description": "통계 데이터 반환 성공"},
        500: {"description": "통계 조회 실패"}
        }
    )
def get_collection_stats(db: db_dep):
    """현재 DB에 저장된 기사 수 및 매체별 분포를 확인합니다."""
    try:
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"통계 조회 실패: {str(e)}")


@router.post("/collect-and-summarize", summary="수집 후 즉시 요약 실행",
             responses={
        200: {"description": "백그라운드 수집 및 요약 시작 성공"},
        500: {"description": "작업 스케줄링 실패"}
        }
    )
async def collect_and_summarize(background_tasks: BackgroundTasks):
    """수집이 끝난 직후 요약을 연속으로 실행합니다."""
    try:
        async def run_full_batch():
            await run_collection_process()
            await run_summary_process(limit=5)

        background_tasks.add_task(run_full_batch)
        return {"message": "수집 및 요약 연속 작업이 백그라운드에서 시작되었습니다."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"작업 등록 실패: {str(e)}")

    
@router.post("/today-briefing", 
             response_model=BatchResponse,
    responses={
        200: {"description": "브리핑 생성 성공 또는 중복 스킵"},
        500: {"description": "서버 내부 오류 (GPT API 실패 또는 DB 제약 조건 위반)"} # 👈 요청하신 부분
    }
    )
async def run_today_briefing(db: db_dep):
    """
    [배치 작업] 오늘의 뉴스 키워드를 분석하여 3분 브리핑을 생성합니다.
    - 중복 체크 로직이 포함되어 있어 하루에 한 번만 생성됩니다.
    - Article 테이블과 연결되지 않은 독립적인 NewsSummary가 생성됩니다.
    """
    try:
        # services/briefing.py에 구현된 핵심 로직 호출
        await create_daily_briefing(db)
        
        # 만약 로직 내부에서 이미 존재하여 None 등을 리턴한다면 그에 맞는 응답
        return {
            "status": "success",
            "message": "오늘의 브리핑 처리 프로세스가 완료되었습니다.",
            "detail": "이미 존재할 경우 생성이 스킵되었을 수 있습니다. 로그를 확인하세요."
        }
    except Exception as e:
        # 실제 500 에러를 던지는 부분
        raise HTTPException(
            status_code=500, 
            detail=f"브리핑 생성 중 오류 발생: {str(e)}"
        )