from sqlalchemy import Column, Integer, String, Date, TIMESTAMP, ForeignKey, UniqueConstraint, text
from app.core.database import Base

class KeywordLog(Base):
    __tablename__ = "KEYWORD_LOG"

    ID = Column(Integer, primary_key=True, autoincrement=True)
    KEYWORD_ID = Column(String(50), ForeignKey("NEWS_KEYWORD.ID", ondelete="CASCADE"), nullable=False)
    TARGET_DATE = Column(Date, nullable=False)
    MENTION_COUNT = Column(Integer, server_default="1")
    CREATED_AT = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    UPDATED_AT = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

    __table_args__ = (UniqueConstraint('KEYWORD_ID', 'TARGET_DATE', name='uq_keyword_date'),)