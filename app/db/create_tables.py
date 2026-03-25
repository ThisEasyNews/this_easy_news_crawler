import sys
import os

# 프로젝트 루트를 경로에 추가 (임포트 에러 방지)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import engine
from app.db.base import Base  # 모든 모델이 모여있는 base.py를 가져옴.

def init_db():
    print("테이블 생성 시작")
    try:
        # Base에 연결된 모든 테이블을 실제 DB에 생성함.
        Base.metadata.create_all(bind=engine)
        print("모든 테이블 생성 완료")
    except Exception as e:
        print(f"❌ 테이블 생성 중 오류 발생: {e}")

if __name__ == "__main__":
    init_db()