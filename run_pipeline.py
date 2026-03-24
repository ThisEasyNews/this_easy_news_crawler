# GitHub Actions가 실행할 통합 배치 스크립트
from app.core.database import SessionLocal
from app.services.collector import collect_news_task

def run():
    db = SessionLocal()
    try:
        print("🚀 배치 프로세스 시작: 뉴스 수집 중...")
        collect_news_task(db)
    finally:
        db.close()

if __name__ == "__main__":
    run()