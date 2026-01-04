"""
Documents Router
Endpoints for document ingestion and management
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, status
from typing import List, Optional
from uuid import UUID
import tempfile
import os

from app.pipelines.rag.ingest import ingest_text, ingest_file, delete_user_documents, is_available

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/ingest")
async def ingest_documents(
    user_id: UUID = Form(...),
    files: List[UploadFile] = File(...)
):
    """
    Ingest documents for RAG.
    
    Accepts multiple files and converts them to vector embeddings.
    Stores in Pinecone with user-scoped namespace.
    
    Supported formats: .txt, .md, .csv (text-based files)
    """
    if not is_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="RAG service not available. Check Pinecone configuration."
        )
    
    results = []
    errors = []
    
    for file in files:
        try:
            # Read file content
            content = await file.read()
            
            # Try to decode as text
            try:
                text = content.decode("utf-8")
            except UnicodeDecodeError:
                try:
                    text = content.decode("latin-1")
                except:
                    errors.append({
                        "file": file.filename,
                        "error": "Could not decode file. Only text-based files are supported."
                    })
                    continue
            
            if not text.strip():
                errors.append({
                    "file": file.filename,
                    "error": "File is empty"
                })
                continue
            
            # Ingest the text
            result = ingest_text(
                text=text,
                user_id=str(user_id),
                source_name=file.filename,
                metadata={"original_filename": file.filename}
            )
            
            if result["success"]:
                results.append({
                    "file": file.filename,
                    "chunks": result["chunks_count"],
                    "status": "success"
                })
            else:
                errors.append({
                    "file": file.filename,
                    "error": result.get("error", "Unknown error")
                })
        
        except Exception as e:
            errors.append({
                "file": file.filename,
                "error": str(e)
            })
    
    return {
        "success": len(results) > 0,
        "ingested": results,
        "errors": errors,
        "total_files": len(files),
        "successful": len(results),
        "failed": len(errors)
    }


@router.post("/ingest-text")
async def ingest_text_content(
    user_id: UUID = Form(...),
    text: str = Form(...),
    source_name: str = Form("manual-input")
):
    """
    Ingest raw text content for RAG.
    
    Useful for ingesting content directly without file upload.
    """
    if not is_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="RAG service not available. Check Pinecone configuration."
        )
    
    if not text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Text content is empty"
        )
    
    result = ingest_text(
        text=text,
        user_id=str(user_id),
        source_name=source_name
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("error", "Ingestion failed")
        )
    
    return result


@router.delete("/{user_id}")
async def delete_documents(user_id: UUID):
    """
    Delete all documents for a user.
    
    Removes all vectors from the user's namespace in Pinecone.
    """
    if not is_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="RAG service not available"
        )
    
    result = delete_user_documents(str(user_id))
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("error", "Deletion failed")
        )
    
    return result


@router.get("/status")
async def get_rag_status():
    """
    Check RAG service status.
    """
    return {
        "available": is_available(),
        "message": "RAG service is ready" if is_available() else "RAG service not configured"
    }
