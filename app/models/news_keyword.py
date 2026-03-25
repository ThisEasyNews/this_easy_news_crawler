from sqlalchemy import Column, Integer, String, TIMESTAMP, text
from app.core.database import Base

class NewsKeyword(Base):
    __tablename__ = "news_keyword"  

    id = Column(Integer, primary_key=True, autoincrement=True)
    keyword = Column(String(50), nullable=False, unique=True)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    status_code = Column(String(50), nullable=False, server_default="PUBLISHED")
    start_date = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    end_date = Column(TIMESTAMP, nullable=False, server_default="'9999-12-31 23:59:59'")