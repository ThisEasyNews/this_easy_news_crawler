from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, text
from app.core.database import Base

class SummaryKeyword(Base):
    __tablename__ = "SUMMARY_KEYWORD"

    ID = Column(Integer, primary_key=True, autoincrement=True)
    SUMMARY_ID = Column(Integer, ForeignKey("NEWS_SUMMARY.ID", ondelete="CASCADE"), nullable=False)
    KEYWORD_ID = Column(String(50), ForeignKey("NEWS_KEYWORD.ID", ondelete="CASCADE"), nullable=False)
    CREATED_AT = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    UPDATED_AT = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))