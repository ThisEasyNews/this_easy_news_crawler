from sqlalchemy import Column, Integer, String, Date, TIMESTAMP, ForeignKey, UniqueConstraint, text
from app.core.database import Base

class KeywordLog(Base):
    __tablename__ = "keyword_log" 

    id = Column(Integer, primary_key=True, autoincrement=True)
    keyword_id = Column(String(50), ForeignKey("news_keyword.id", ondelete="CASCADE"), nullable=False)
    target_date = Column(Date, nullable=False)
    mention_count = Column(Integer, server_default="1")
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

    __table_args__ = (
        UniqueConstraint('keyword_id', 'target_date', name='uq_keyword_date'),
    )