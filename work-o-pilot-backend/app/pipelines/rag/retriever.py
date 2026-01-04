"""
RAG Retriever Service
Queries Pinecone for relevant document chunks
Adapted from Project-3
"""
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
from app.core.config import settings
from typing import List, Optional

# Lazy initialization
_pc = None
_index = None
_embedder = None


def _init_pinecone():
    """Initialize Pinecone client (lazy loading)."""
    global _pc, _index, _embedder
    
    if _pc is not None:
        return True
    
    if not settings.PINECONE_API_KEY:
        print("[RAG Retriever] Pinecone API key not configured")
        return False
    
    try:
        _pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        
        # Check if index exists
        existing_indexes = _pc.list_indexes().names()
        
        if settings.PINECONE_INDEX not in existing_indexes:
            print(f"[RAG Retriever] Index {settings.PINECONE_INDEX} not found")
            return False
        
        _index = _pc.Index(settings.PINECONE_INDEX)
        _embedder = SentenceTransformer("all-MiniLM-L6-v2")
        
        print("[RAG Retriever] Initialized successfully")
        return True
        
    except Exception as e:
        print(f"[RAG Retriever] Init error: {e}")
        return False


def is_available() -> bool:
    """Check if retriever is available."""
    return _init_pinecone()


def retrieve(
    query: str,
    user_id: str,
    top_k: int = 10
) -> List[dict]:
    """
    Retrieve relevant documents for a query.
    
    Args:
        query: Search query
        user_id: User ID for namespace scoping
        top_k: Number of results to return
    
    Returns:
        List of matching document chunks with metadata
    """
    if not _init_pinecone():
        return []
    
    try:
        # Generate query embedding
        query_embedding = _embedder.encode(query).tolist()
        
        # Query user's namespace
        namespace = f"user-{user_id}"
        
        results = _index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True,
            namespace=namespace
        )
        
        matches = results.get("matches", [])
        print(f"[RAG Retriever] Found {len(matches)} matches for query")
        
        return matches
    
    except Exception as e:
        print(f"[RAG Retriever] Query error: {e}")
        return []


def format_context(matches: List[dict]) -> str:
    """
    Format retrieved matches into context string for LLM.
    
    Args:
        matches: List of Pinecone match results
    
    Returns:
        Formatted context string
    """
    if not matches:
        return ""
    
    context_parts = []
    for i, match in enumerate(matches):
        metadata = match.get("metadata", {})
        text = metadata.get("text", "")
        source = metadata.get("source", "Unknown")
        
        context_parts.append(f"[Source: {source}]\n{text}")
    
    return "\n\n---\n\n".join(context_parts)


def get_sources(matches: List[dict]) -> List[dict]:
    """
    Extract source information from matches.
    
    Args:
        matches: List of Pinecone match results
    
    Returns:
        List of source dicts
    """
    sources = []
    seen = set()
    
    for match in matches:
        metadata = match.get("metadata", {})
        source = metadata.get("source", "Unknown")
        
        if source not in seen:
            seen.add(source)
            sources.append({
                "name": source,
                "type": "document",
                "chunk_count": 1
            })
        else:
            # Increment chunk count for existing source
            for s in sources:
                if s["name"] == source:
                    s["chunk_count"] += 1
                    break
    
    return sources
