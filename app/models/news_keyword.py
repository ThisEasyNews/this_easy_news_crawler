from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, text
from app.core.database import Base

class NewsKeyword(Base):
    __tablename__ = "NEWS_KEYWORD"

    ID = Column(String(50), primary_key=True)
    KEYWORD = Column(String(50), nullable=False, unique=True)
    CREATED_AT = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    UPDATED_AT = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    STATUS_CODE = Column(String(50), nullable=False, server_default="PUBLISHED")
    START_DATE = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    END_DATE = Column(TIMESTAMP, nullable=False, server_default="'9999-12-31 23:59:59'")