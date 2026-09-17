from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import api_router
from app.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="SkyNest Hotel Reservation & Guest Services Management System API",
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API v1 routes
app.include_router(api_router)


@app.get("/")
def root():
    return {
        "message": "Welcome to SkyNest Hotels API",
        "docs_url": "/docs",
        "version": settings.APP_VERSION,
    }


@app.get("/health")
def health():
    return {"status": "healthy"}
