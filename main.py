from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from app.database.database import Base, engine, get_db
from app.routers import user, issue
from app.core.websocket import manager
from app.core.dependencies import get_current_user
from sqlalchemy.orm import Session
import logging
from sqlalchemy import text # Import text for raw SQL execution

# Import your enum classes from models
from app.models.models import UserRole, IssueStatus, IssueSeverity

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Issues & Insights Tracker API",
    description="A comprehensive issue tracking system with user management",
    version="1.0.0"
)

# NEW: Robustly create database enum types and tables on startup
@app.on_event("startup")
def startup_event():
    logger.info("Ensuring database enum types and tables exist...")
    
    # Get a connection to execute raw SQL for enum types
    with engine.connect() as connection:
        # Create UserRole enum type if it doesn't exist
        user_role_values = ", ".join([f"'{role.value}'" for role in UserRole])
        connection.execute(text(f"""
            DO $$ BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'userrole') THEN
                    CREATE TYPE userrole AS ENUM ({user_role_values});
                END IF;
            END $$;
        """))
        
        # Create IssueStatus enum type if it doesn't exist
        issue_status_values = ", ".join([f"'{status.value}'" for status in IssueStatus])
        connection.execute(text(f"""
            DO $$ BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'issuestatus') THEN
                    CREATE TYPE issuestatus AS ENUM ({issue_status_values});
                END IF;
            END $$;
        """))

        # Create IssueSeverity enum type if it doesn't exist
        issue_severity_values = ", ".join([f"'{severity.value}'" for severity in IssueSeverity])
        connection.execute(text(f"""
            DO $$ BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'issueseverity') THEN
                    CREATE TYPE issueseverity AS ENUM ({issue_severity_values});
                END IF;
            END $$;
        """))
        
        connection.commit() # Commit the enum type creation

    # Now, create all tables (which might depend on the enums)
    Base.metadata.create_all(bind=engine)
    logger.info("Database enum types and tables ensured.")

# Include routers
app.include_router(user.router)
app.include_router(issue.router)

# WebSocket endpoint for real-time updates
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and listen for client messages
            data = await websocket.receive_text()
            logger.info(f"Received WebSocket message: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Test route
@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Issues & Insights Tracker backend is running 🚀"}