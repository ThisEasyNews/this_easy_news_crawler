# 환경 변수 (DB_URL, OpenAI_KEY 등)
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # 프로젝트 이름
    PROJECT_NAME: str = "This Easy News Crawler"
    
    # DB 접속 정보 (환경 변수가 없으면 기본 로컬 DB 사용)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    
    # OpenAI API 키
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    class Config:
        # .env 파일을 자동으로 읽어오도록 설정
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # .env 파일이 없어도 에러를 내지 않도록 설정 (GitHub Actions 환경 대응)

# 중요: 이 라인이 있어야 다른 파일에서 'from app.core.config import settings'이 가능
settings = Settings()

if not settings.DATABASE_URL:
    print("⚠️ 경고: DATABASE_URL 환경 변수를 찾을 수 없습니다!")