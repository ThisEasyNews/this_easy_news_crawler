from sqlalchemy import Column, Integer, String, TIMESTAMP, Date, Text, text, ForeignKey
from app.core.database import Base

class NewsSummary(Base):
    __tablename__ = "news_summary"  

    id = Column(Integer, primary_key=True, autoincrement=True)
    summary_type = Column(String(50), nullable=False, server_default="GENERAL")
    title = Column(String(1000), nullable=False)
    summary_content = Column(Text, nullable=False)
    insight = Column(Text)
    ai_model = Column(String(50))
    top_image_url = Column(String(5000))
    view_count = Column(Integer, server_default="0")
    target_date = Column(Date)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    status_code = Column(String(50), nullable=False, server_default="PUBLISHED")
    start_date = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    end_date = Column(TIMESTAMP, nullable=False, server_default="'9999-12-31 23:59:59'")