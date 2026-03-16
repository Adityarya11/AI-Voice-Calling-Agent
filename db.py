import os
import datetime
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./riverwood.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    phone = Column(String)
    language = Column(String)
    project = Column(String)
    unit = Column(String)
    booking_date = Column(String)
    payment_status = Column(String)
    site_visit_interest = Column(Boolean, default=False)

class ConstructionUpdate(Base):
    __tablename__ = "construction_updates"
    project = Column(String, primary_key=True, index=True)
    update_id = Column(String)
    current_phase = Column(String)
    completion_percentage = Column(Integer)
    recent_milestone = Column(Text)
    next_milestone = Column(Text)
    expected_completion = Column(String)
    site_visit_available = Column(Boolean, default=False)
    site_visit_timings = Column(String, nullable=True)

class Interaction(Base):
    __tablename__ = "interactions"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String, index=True)
    role = Column(String)
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class CallLog(Base):
    __tablename__ = "call_logs"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String, index=True)
    status = Column(String)
    audio_path = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)