from sqlalchemy import TIMESTAMP, Column, ForeignKey, String, Text, DateTime, text
from datetime import datetime
from app.core.database import Base

class CommonDetail(Base):
    __tablename__ = "COMMON_DETAIL"

    ID = Column(String(50), primary_key=True)
    GROUP_ID = Column(String(50), ForeignKey("COMMON_GROUP.ID"), nullable=False)
    NAME = Column(String(50), nullable=False)
    CODE_VALUE = Column(String(5000))
    CREATED_AT = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    UPDATED_AT = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    STATUS_CODE = Column(String(50), nullable=False, server_default="PUBLISHED")
    START_DATE = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    END_DATE = Column(TIMESTAMP, nullable=False, server_default="'9999-12-31 23:59:59'")