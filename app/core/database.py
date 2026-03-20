from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings # 환경설정 파일에서 DB 주소를 가져옴

# 1. DB 접속 엔진 생성 (통로 개설)
# settings.DATABASE_URL: .env에 작성한 접속 주소
engine = create_engine(settings.DATABASE_URL)

# 2. 세션 팩토리 생성 (대기소)
# 각 요청마다 독립적인 DB 작업 단위를 제공합니다.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 3. 선언적 베이스 클래스 (모든 모델의 부모)
# 이 Base를 상속받아야 DB 테이블로 인식됩니다.
Base = declarative_base()

# 4. DB 세션 의존성 (Dependency Injection용)
# FastAPI에서 각 API 호출 시 DB를 안전하게 열고 닫아줍니다.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()