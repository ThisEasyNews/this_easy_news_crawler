from sqlalchemy import Column, Integer, String, TIMESTAMP, Text, text
from app.core.database import Base

class BatchLog(Base):
    __tablename__ = "BATCH_LOG"

    ID = Column(Integer, primary_key=True, autoincrement=True)
    JOB_NAME = Column(String(100), nullable=False)
    START_TIME = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    END_TIME = Column(TIMESTAMP)
    STATUS_CODE = Column(String(20), nullable=False)
    TOTAL_COUNT = Column(Integer, server_default="0")
    SUCCESS_COUNT = Column(Integer, server_default="0")
    FAIL_COUNT = Column(Integer, server_default="0")
    ERROR_MESSAGE = Column(Text)
    EXECUTION_TIME_SEC = Column(Integer)
    CREATED_AT = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    UPDATED_AT = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))