from sqlalchemy import Column, Integer, String, TIMESTAMP, Text, text
from app.core.database import Base

class BatchLog(Base):
    __tablename__ = "batch_log"  

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_name = Column(String(100), nullable=False)
    start_time = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    end_time = Column(TIMESTAMP)
    status_code = Column(String(20), nullable=False)  # 예: 'SUCCESS', 'FAIL', 'RUNNING'
    total_count = Column(Integer, server_default="0")
    success_count = Column(Integer, server_default="0")
    fail_count = Column(Integer, server_default="0")
    error_message = Column(Text)
    execution_time_sec = Column(Integer)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))