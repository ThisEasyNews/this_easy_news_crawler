from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, Boolean, ForeignKey, text
from app.core.database import Base

class Article(Base):
    __tablename__ = "article"  

    id = Column(Integer, primary_key=True, autoincrement=True)
    media_id = Column(String(50), ForeignKey("common_detail.id"))
    category_id = Column(String(50), ForeignKey("common_detail.id"))
    original_title = Column(String(1000), nullable=False)
    url = Column(String(5000), nullable=False, unique=True)
    feedparser_content = Column(Text)       
    crawler_content = Column(Text)          
    description = Column(Text)              
    image_url = Column(String(5000))
    published_at = Column(TIMESTAMP)
    scraped_at = Column(TIMESTAMP)
    is_summarized = Column(Boolean, server_default="false") 
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    status_code = Column(String(50), nullable=False, server_default="PUBLISHED")
    start_date = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    end_date = Column(TIMESTAMP, nullable=False, server_default="'9999-12-31 23:59:59'")