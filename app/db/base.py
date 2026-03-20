# DB 연결 및 세션 관리 (SQLAlchemy)
# 모든 모델을 통합 관리 (Alembic용)

# 1. 공통 베이스 클래스 가져오기. database.py에서 정의한 것
from app.core.database import Base

# 2. 모든 모델을 여기에 import하기. SQLALchemy가 어떤 테이블을 만들어야 할지 인지함.
from app.models.common.common_group import CommonGroup
from app.models.common.common_detail import CommonDetail
from app.models.article import Article
from app.models.batch_log import BatchLog
from app.models.briefing_summary import BriefingSummary
from app.models.keyword_log import KeywordLog
from app.models.news_keyword import NewsKeyword
from app.models.news_summary import NewsSummary
from app.models.summary_keyword import SummaryKeyword