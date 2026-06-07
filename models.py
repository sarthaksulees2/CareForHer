"""
SQLAlchemy Models for MHM Hub
Tables: User and PeriodTrackHistory
"""

from db_config import Base
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from datetime import datetime

class User(Base):
    """User table for MHM Hub"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    phone = Column(String(20), unique=True, nullable=True, index=True)
    password = Column(String(255), nullable=False)
    
    age = Column(Integer, nullable=True)
    gender = Column(String(20), nullable=True)
    height = Column(Float, nullable=True)  # in cm
    weight = Column(Float, nullable=True)  # in kg
    
    cycle_length = Column(Integer, default=28)  # Average cycle length in days
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<User(id={self.id}, name={self.name}, email={self.email})>"


class PeriodTrackHistory(Base):
    """Period tracking history table"""
    __tablename__ = "period_track_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    last_period_date = Column(DateTime, nullable=False)
    period_end_date = Column(DateTime, nullable=True)
    cycle_length = Column(Integer, nullable=False)
    next_period_predicted = Column(DateTime, nullable=False)
    
    period_symptoms = Column(Text, nullable=True)  # JSON or comma-separated symptoms
    flow_intensity = Column(String(20), nullable=True)  # light, medium, heavy
    mood = Column(String(50), nullable=True)
    energy_level = Column(Integer, nullable=True)  # 1-10 scale
    notes = Column(Text, nullable=True)
    
    recorded_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<PeriodTrackHistory(id={self.id}, user_id={self.user_id}, last_period={self.last_period_date})>"
