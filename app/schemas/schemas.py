from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
from app.models.models import UserRole, IssueStatus, IssueSeverity

# -------------------------
# User Schemas
# -------------------------

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str
    role: Optional[UserRole] = UserRole.REPORTER

class UserResponse(UserBase):
    id: int
    role: UserRole
    created_at: datetime

    class Config:
        from_attributes = True  # Updated for Pydantic v2

# -------------------------
# Issue Schemas
# -------------------------

class IssueBase(BaseModel):
    title: str
    description: Optional[str] = None
    severity: Optional[IssueSeverity] = IssueSeverity.MEDIUM
    tags: Optional[str] = None

class IssueCreate(IssueBase):
    pass

class IssueUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[IssueStatus] = None
    severity: Optional[IssueSeverity] = None
    tags: Optional[str] = None

class IssueResponse(IssueBase):
    id: int
    status: IssueStatus
    owner_id: int
    file_path: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    owner: UserResponse

    class Config:
        from_attributes = True

# -------------------------
# Auth Schemas
# -------------------------

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# NEW SCHEMA: TokenData (for JWT payload)
class TokenData(BaseModel):
    email: Optional[str] = None
    # You might also include other fields from your JWT payload, e.g.,
    # roles: Optional[str] = None # if you store roles directly in the token sub field

# -------------------------
# Dashboard & Stats Schemas
# -------------------------

class DashboardStats(BaseModel):
    total_issues: int
    open_issues: int
    severity_breakdown: dict
    status_breakdown: dict

class WebSocketMessage(BaseModel):
    type: str  # "issue_created", "issue_updated", "issue_deleted"
    data: dict
    