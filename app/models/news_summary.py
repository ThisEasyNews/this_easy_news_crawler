from sqlalchemy import TIMESTAMP, Column, Date, Integer, String, Text, text
from app.core.database import Base

class NewsSummary(Base):
    __tablename__ = "NEWS_SUMMARY"

    ID = Column(Integer, primary_key=True, autoincrement=True)
    SUMMARY_TYPE = Column(String(50), nullable=False, server_default="GENERAL")
    TITLE = Column(String(1000), nullable=False)
    SUMMARY_CONTENT = Column(Text, nullable=False)
    INSIGHT = Column(Text)
    AI_MODEL = Column(String(50))
    TOP_IMAGE_URL = Column(String(5000))
    VIEW_COUNT = Column(Integer, server_default="0")
    TARGET_DATE = Column(Date)
    CREATED_AT = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    UPDATED_AT = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    STATUS_CODE = Column(String(50), nullable=False, server_default="PUBLISHED")
    START_DATE = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    END_DATE = Column(TIMESTAMP, nullable=False, server_default="'9999-12-31 23:59:59'")