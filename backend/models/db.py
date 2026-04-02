"""
Database Models for Hand Hygiene System
Using PostgreSQL with SQLAlchemy ORM
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON

db = SQLAlchemy()


class HygieneEvent(db.Model):
    """
    Model for hand hygiene events
    Records each handwashing event with duration and compliance status
    """
    __tablename__ = 'hygiene_events'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(255), nullable=False, default='system')
    start_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    end_time = db.Column(db.DateTime, nullable=True)
    duration = db.Column(db.Float, nullable=False)  # in seconds
    status = db.Column(db.String(50), nullable=False)  # 'completed' or 'incomplete'
    compliance = db.Column(db.Boolean, default=False)  # True if >= 20 seconds
    location = db.Column(db.String(255), nullable=True)
    department = db.Column(db.String(255), nullable=True)
    event_metadata = db.Column(JSON, nullable=True)  # Additional data
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration': round(self.duration, 1),
            'status': self.status,
            'compliance': self.compliance,
            'location': self.location,
            'department': self.department,
            'event_metadata': self.event_metadata,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<HygieneEvent {self.id}: {self.status} ({self.duration}s)>'


class DailyStats(db.Model):
    """
    Model for daily compliance statistics
    Aggregated data for faster analytics queries
    """
    __tablename__ = 'daily_stats'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, unique=True)
    total_events = db.Column(db.Integer, default=0)
    completed_events = db.Column(db.Integer, default=0)
    incomplete_events = db.Column(db.Integer, default=0)
    compliance_rate = db.Column(db.Float, default=0.0)  # percentage
    avg_duration = db.Column(db.Float, default=0.0)  # seconds
    total_duration = db.Column(db.Float, default=0.0)  # seconds
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'date': self.date.isoformat() if self.date else None,
            'total_events': self.total_events,
            'completed_events': self.completed_events,
            'incomplete_events': self.incomplete_events,
            'compliance_rate': round(self.compliance_rate, 2),
            'avg_duration': round(self.avg_duration, 1),
            'total_duration': round(self.total_duration, 1),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<DailyStats {self.date}: {self.compliance_rate}%>'


class User(db.Model):
    """
    Model for users (healthcare workers)
    """
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    department = db.Column(db.String(255), nullable=True)
    role = db.Column(db.String(100), nullable=True)  # doctor, nurse, etc
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'department': self.department,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<User {self.user_id}: {self.name}>'


def init_db(app):
    """Initialize database with Flask app"""
    db.init_app(app)
    with app.app_context():
        db.create_all()
