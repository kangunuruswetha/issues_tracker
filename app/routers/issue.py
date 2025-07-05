from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.schemas.schemas import IssueCreate, IssueResponse, IssueUpdate, DashboardStats
from app.models.models import Issue, User, UserRole, IssueStatus, IssueSeverity
from app.database.database import get_db
from typing import List, Optional
from app.core.dependencies import get_current_user, require_role, require_maintainer_or_admin
import os
import uuid
from pathlib import Path

router = APIRouter(prefix="/issues", tags=["Issues"])

# File upload directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@router.post("/", response_model=IssueResponse)
def create_issue(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    severity: IssueSeverity = Form(IssueSeverity.MEDIUM),
    tags: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Handle file upload
    file_path = None
    if file:
        file_extension = Path(file.filename).suffix
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = UPLOAD_DIR / unique_filename
        
        with open(file_path, "wb") as buffer:
            content = file.file.read()
            buffer.write(content)
        
        file_path = str(file_path)
    
    new_issue = Issue(
        title=title,
        description=description,
        severity=severity,
        tags=tags,
        file_path=file_path,
        owner_id=current_user.id
    )
    db.add(new_issue)
    db.commit()
    db.refresh(new_issue)
    return new_issue

@router.get("/", response_model=List[IssueResponse])
def get_issues(
    status: Optional[IssueStatus] = None,
    severity: Optional[IssueSeverity] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Issue)
    
    # Apply role-based filtering
    if current_user.role == UserRole.REPORTER:
        query = query.filter(Issue.owner_id == current_user.id)
    
    # Apply optional filters
    if status:
        query = query.filter(Issue.status == status)
    if severity:
        query = query.filter(Issue.severity == severity)
    
    return query.all()

@router.get("/{issue_id}", response_model=IssueResponse)
def get_issue(
    issue_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    
    # Check access rights
    if current_user.role == UserRole.REPORTER and issue.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return issue

@router.put("/{issue_id}", response_model=IssueResponse)
def update_issue(
    issue_id: int,
    issue_update: IssueUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    
    # Check access rights
    if current_user.role == UserRole.REPORTER:
        # Reporters can only update their own issues and only title/description
        if issue.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        # Reporters cannot change status
        if issue_update.status is not None:
            raise HTTPException(status_code=403, detail="Reporters cannot change issue status")
    
    # Update fields
    update_data = issue_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(issue, field, value)
    
    db.commit()
    db.refresh(issue)
    return issue

@router.delete("/{issue_id}")
def delete_issue(
    issue_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    
    # Delete file if exists
    if issue.file_path and os.path.exists(issue.file_path):
        os.remove(issue.file_path)
    
    db.delete(issue)
    db.commit()
    return {"message": "Issue deleted successfully"}

@router.get("/dashboard/stats", response_model=DashboardStats)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Issue)
    
    # Apply role-based filtering
    if current_user.role == UserRole.REPORTER:
        query = query.filter(Issue.owner_id == current_user.id)
    
    issues = query.all()
    
    total_issues = len(issues)
    open_issues = len([i for i in issues if i.status == IssueStatus.OPEN])
    
    severity_breakdown = {
        "low": len([i for i in issues if i.severity == IssueSeverity.LOW]),
        "medium": len([i for i in issues if i.severity == IssueSeverity.MEDIUM]),
        "high": len([i for i in issues if i.severity == IssueSeverity.HIGH]),
        "critical": len([i for i in issues if i.severity == IssueSeverity.CRITICAL])
    }
    
    status_breakdown = {
        "open": len([i for i in issues if i.status == IssueStatus.OPEN]),
        "triaged": len([i for i in issues if i.status == IssueStatus.TRIAGED]),
        "in_progress": len([i for i in issues if i.status == IssueStatus.IN_PROGRESS]),
        "done": len([i for i in issues if i.status == IssueStatus.DONE])
    }
    
    return DashboardStats(
        total_issues=total_issues,
        open_issues=open_issues,
        severity_breakdown=severity_breakdown,
        status_breakdown=status_breakdown
    )

