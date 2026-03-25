from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, text
from app.core.database import Base

class SummaryKeyword(Base):
    __tablename__ = "summary_keyword" 

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    summary_id = Column(Integer, ForeignKey("news_summary.id", ondelete="CASCADE"), nullable=False)
    keyword_id = Column(String(50), ForeignKey("news_keyword.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))