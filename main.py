from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from app.database.database import Base, engine, get_db
from app.routers import user, issue
from app.core.websocket import manager
from app.core.dependencies import get_current_user
from sqlalchemy.orm import Session
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Issues & Insights Tracker API",
    description="A comprehensive issue tracking system with user management",
    version="1.0.0"
)

# Include routers
app.include_router(user.router)
app.include_router(issue.router)

# Create tables on startup (auto-generates from SQLAlchemy models)
Base.metadata.create_all(bind=engine)

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
