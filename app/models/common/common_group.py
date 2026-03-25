from sqlalchemy import Column, String, TIMESTAMP, text
from app.core.database import Base

class CommonGroup(Base):
    __tablename__ = "common_group"  

    id = Column(String(50), primary_key=True)
    name = Column(String(50), nullable=False)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    status_code = Column(String(50), nullable=False, server_default="PUBLISHED")
    start_date = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    end_date = Column(TIMESTAMP, nullable=False, server_default="'9999-12-31 23:59:59'")