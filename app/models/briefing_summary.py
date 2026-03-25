from sqlalchemy import Column, ForeignKey, Integer, TIMESTAMP, text
from app.core.database import Base

class BriefingSummary(Base):
    __tablename__ = "briefing_summary"  

    id = Column(Integer, primary_key=True, autoincrement=True)
    briefing_id = Column(Integer, ForeignKey("news_summary.id", ondelete="CASCADE"))
    summary_id = Column(Integer, ForeignKey("news_summary.id", ondelete="CASCADE"))
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))