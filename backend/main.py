from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from app.core.config import settings
from app.core.database import connect_to_mongo, close_mongo_connection


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    
    # Initialize and start email queue
    from app.services.email_queue import get_email_queue
    from app.services.email_service import EmailService
    
    # Initialize email service (this will set up the queue)
    email_service = EmailService()
    email_queue = get_email_queue()
    await email_queue.start()
    
    # Import API modules after database connection
    from app.api import auth, users, requests, donations, comments, notifications, chat, ai, admin, webhooks
    from app.api.websocket import socket_app
    
    # Include API routers
    app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
    app.include_router(users.router, prefix="/api/users", tags=["Users"])
    app.include_router(requests.router, prefix="/api/requests", tags=["Requests"])
    app.include_router(donations.router, prefix="/api/donations", tags=["Donations"])
    app.include_router(comments.router, prefix="/api/comments", tags=["Comments"])
    app.include_router(notifications.router, prefix="/api/notifications", tags=["Notifications"])
    app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
    app.include_router(ai.router, prefix="/api/ai", tags=["AI"])
    app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
    app.include_router(webhooks.router, prefix="/api/webhooks", tags=["Webhooks"])
    
    # Mount Socket.IO app
    app.mount("/socket.io", socket_app)
    
    yield
    # Shutdown
    # Stop email queue gracefully
    await email_queue.stop()
    await close_mongo_connection()


# Create FastAPI app
app = FastAPI(
    title="Blood Bank API",
    description="FastAPI backend for Blood Bank App with MongoDB, JWT auth, WebSocket, and AI integration",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
    # allow_origins=settings.cors_origins,
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get("/")
async def root():
    return {"message": "Blood Bank API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API is running"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
