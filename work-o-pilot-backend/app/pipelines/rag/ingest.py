"""
RAG Ingest Service
Converts documents to vector embeddings and stores in Pinecone
Adapted from Project-3
"""
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
from app.core.config import settings
from typing import List, Optional
import uuid
import os

# Lazy initialization to avoid startup errors if Pinecone not configured
_pc = None
_index = None
_embedder = None
_splitter = None


def _init_pinecone():
    """Initialize Pinecone client and index (lazy loading)."""
    global _pc, _index, _embedder, _splitter
    
    if _pc is not None:
        return True
    
    if not settings.PINECONE_API_KEY:
        print("[RAG] Pinecone API key not configured")
        return False
    
    try:
        _pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        
        # Check if index exists, create if not
        existing_indexes = _pc.list_indexes().names()
        
        if settings.PINECONE_INDEX not in existing_indexes:
            _pc.create_index(
                name=settings.PINECONE_INDEX,
                dimension=384,  # all-MiniLM-L6-v2 embedding dimension
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-east-1"
                )
            )
            print(f"[RAG] Created Pinecone index: {settings.PINECONE_INDEX}")
        else:
            print(f"[RAG] Using existing index: {settings.PINECONE_INDEX}")
        
        _index = _pc.Index(settings.PINECONE_INDEX)
        _embedder = SentenceTransformer("all-MiniLM-L6-v2")
        _splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=100
        )
        
        print("[RAG] Pinecone initialized successfully")
        return True
        
    except Exception as e:
        print(f"[RAG] Failed to initialize Pinecone: {e}")
        return False


def is_available() -> bool:
    """Check if RAG services are available."""
    return _init_pinecone()


def ingest_text(
    text: str,
    user_id: str,
    source_name: str,
    metadata: dict = None
) -> dict:
    """
    Ingest a text document into Pinecone.
    
    Args:
        text: Document text content
        user_id: User ID for namespace isolation
        source_name: Name of the source document
        metadata: Additional metadata to store
    
    Returns:
        Dict with ingestion results
    """
    if not _init_pinecone():
        return {"success": False, "error": "RAG services not available"}
    
    try:
        # Split text into chunks
        chunks = _splitter.split_text(text)
        
        if not chunks:
            return {"success": False, "error": "No text content to ingest"}
        
        vectors = []
        for i, chunk in enumerate(chunks):
            vector_id = str(uuid.uuid4())
            embedding = _embedder.encode(chunk).tolist()
            
            chunk_metadata = {
                "text": chunk,
                "source": source_name,
                "chunk_id": i,
                "user_id": user_id
            }
            
            # Add custom metadata if provided
            if metadata:
                chunk_metadata.update(metadata)
            
            vectors.append({
                "id": vector_id,
                "values": embedding,
                "metadata": chunk_metadata
            })
        
        # Use user_id as namespace for isolation
        namespace = f"user-{user_id}"
        _index.upsert(vectors, namespace=namespace)
        
        print(f"[RAG] Ingested {len(vectors)} chunks for {source_name}")
        
        return {
            "success": True,
            "chunks_count": len(vectors),
            "source": source_name,
            "namespace": namespace
        }
    
    except Exception as e:
        print(f"[RAG] Ingest error: {e}")
        return {"success": False, "error": str(e)}


def ingest_file(
    file_path: str,
    user_id: str,
    metadata: dict = None
) -> dict:
    """
    Ingest a file into Pinecone.
    
    Args:
        file_path: Path to the file
        user_id: User ID for namespace isolation
        metadata: Additional metadata
    
    Returns:
        Dict with ingestion results
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
        
        source_name = os.path.basename(file_path)
        return ingest_text(text, user_id, source_name, metadata)
    
    except Exception as e:
        print(f"[RAG] File read error: {e}")
        return {"success": False, "error": f"Failed to read file: {e}"}


def delete_user_documents(user_id: str) -> dict:
    """
    Delete all documents for a user.
    
    Args:
        user_id: User ID
    
    Returns:
        Dict with deletion results
    """
    if not _init_pinecone():
        return {"success": False, "error": "RAG services not available"}
    
    try:
        namespace = f"user-{user_id}"
        _index.delete(delete_all=True, namespace=namespace)
        return {"success": True, "message": f"Deleted all documents for user {user_id}"}
    except Exception as e:
        return {"success": False, "error": str(e)}
