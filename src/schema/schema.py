from datetime import datetime
from sqlalchemy import BIGINT, Column, DateTime, VARCHAR, ARRAY, Enum
from sqlalchemy.ext.declarative import declarative_base
from src.configs.enums import ApplicationStatus
from src.configs.constants import DBTables, DBConfig

Base = declarative_base()

class UserModel(Base):
    __tablename__ = DBTables.USERS
    __table_args__ = DBConfig.BASE_ARGS

    id              = COLUMN(BIGINT, primary_key=True, autoincrement=True)
    email           = Column(VARCHAR(256), nullable=False, unique=True)
    password_hash   = Column(VARCHAR(512), nullable=False)
    created_at      = Column(DateTime, default=datetime.utcnow)