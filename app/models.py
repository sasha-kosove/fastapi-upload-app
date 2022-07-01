from sqlalchemy import Column, DateTime, Integer, String

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)


class Frame(Base):
    __tablename__ = "inbox"

    id = Column(Integer, primary_key=True, index=True)
    frame_name = Column(String, index=True)
    registered_at = Column(DateTime, index=True)
