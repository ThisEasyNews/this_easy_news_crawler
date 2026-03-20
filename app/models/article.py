from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, Boolean, ForeignKey, text
from app.core.database import Base

class Article(Base):
    __tablename__ = "ARTICLE"

    ID = Column(Integer, primary_key=True, autoincrement=True)
    SUMMARY_ID = Column(Integer, ForeignKey("NEWS_SUMMARY.ID"))
    MEDIA_ID = Column(String(50), ForeignKey("COMMON_DETAIL.ID"))
    CATEGORY_ID = Column(String(50), ForeignKey("COMMON_DETAIL.ID"))
    ORIGINAL_TITLE = Column(String(1000), nullable=False)
    URL = Column(String(5000), nullable=False, unique=True)
    CONTENT = Column(Text)
    PUBLISHED_AT = Column(TIMESTAMP)
    SCRAPED_AT = Column(TIMESTAMP)
    IS_SUMMARIZED = Column(Boolean, server_default="FALSE")
    CREATED_AT = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    UPDATED_AT = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    STATUS_CODE = Column(String(50), nullable=False, server_default="PUBLISHED")
    START_DATE = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    END_DATE = Column(TIMESTAMP, nullable=False, server_default="'9999-12-31 23:59:59'")