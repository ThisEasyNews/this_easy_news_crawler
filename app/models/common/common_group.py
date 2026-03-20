from sqlalchemy import TIMESTAMP, Column, String, Text, DateTime, text
from datetime import datetime
from app.core.database import Base

class CommonGroup(Base):
    __tablename__ = "COMMON_GROUP"

    ID = Column(String(50), primary_key=True)
    NAME = Column(String(50), nullable=False)
    CREATED_AT = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    UPDATED_AT = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    STATUS_CODE = Column(String(50), nullable=False, server_default="PUBLISHED")
    START_DATE = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    END_DATE = Column(TIMESTAMP, nullable=False, server_default="'9999-12-31 23:59:59'")