# briefing_summary 테이블
from sqlalchemy import Column, ForeignKey, Integer, TIMESTAMP, text
from app.core.database import Base

class BriefingSummary(Base):
    __tablename__ = "BRIEFING_SUMMARY"

    ID = Column(Integer, primary_key=True, autoincrement=True)
    BRIEFING_ID = Column(Integer, ForeignKey("NEWS_SUMMARY.ID", ondelete="CASCADE"))
    SUMMARY_ID = Column(Integer, ForeignKey("NEWS_SUMMARY.ID", ondelete="CASCADE"))
    CREATED_AT = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    UPDATED_AT = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))