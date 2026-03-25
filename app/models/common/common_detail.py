from sqlalchemy import Column, String, TIMESTAMP, ForeignKey, text
from app.core.database import Base

class CommonDetail(Base):
    __tablename__ = "common_detail"  

    id = Column(String(50), primary_key=True)
    group_id = Column(String(50), ForeignKey("common_group.id"), nullable=False)
    
    name = Column(String(50), nullable=False)
    code_value = Column(String(5000))  # RSS URL 등이 저장되는 컬럼
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    status_code = Column(String(50), nullable=False, server_default="PUBLISHED")
    start_date = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    end_date = Column(TIMESTAMP, nullable=False, server_default="'9999-12-31 23:59:59'")