from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.services.supabase_client import supabase
from app.routers import assets, chat, documents, export

app = FastAPI(
    title="Work-o-Pilot Backend",
    description="Stock Analytics AI Copilot API",
    version="1.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(assets.router)
app.include_router(chat.router)
app.include_router(documents.router)
app.include_router(export.router)

@app.get("/")
def read_root():
    return {"message": "Work-o-Pilot Backend", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "ok", "supabase_connected": supabase is not None}

