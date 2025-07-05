from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime, Enum
from sqlalchemy.orm import relationship
from app.database.database import Base
from datetime import datetime
import enum

# Role enum
class UserRole(str, enum.Enum):
    ADMIN = "admin"
    MAINTAINER = "maintainer"
    REPORTER = "reporter"

# Issue status enum
class IssueStatus(str, enum.Enum):
    OPEN = "open"
    TRIAGED = "triaged"
    IN_PROGRESS = "in_progress"
    DONE = "done"

# Issue severity enum
class IssueSeverity(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

# User model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    role = Column(Enum(UserRole), default=UserRole.REPORTER)
    created_at = Column(DateTime, default=datetime.utcnow)

    issues = relationship("Issue", back_populates="owner")

# Issue model
class Issue(Base):
    __tablename__ = "issues"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(IssueStatus), default=IssueStatus.OPEN)
    severity = Column(Enum(IssueSeverity), default=IssueSeverity.MEDIUM)
    file_path = Column(String, nullable=True)  # For file uploads
    tags = Column(String, nullable=True)  # Comma-separated tags
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="issues")

# Daily stats model for background jobs
class DailyStats(Base):
    __tablename__ = "daily_stats"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, nullable=False)
    open_count = Column(Integer, default=0)
    triaged_count = Column(Integer, default=0)
    in_progress_count = Column(Integer, default=0)
    done_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)