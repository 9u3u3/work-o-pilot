"""
RAG Pipeline Executor
Handles document-based Q&A using retrieved context
"""
from typing import Dict, Any, List
from app.pipelines.rag.retriever import retrieve, format_context, get_sources, is_available
from app.services.groq_client import groq_client
from app.services.supabase_client import supabase


RAG_SYSTEM_PROMPT = """You are a personal financial document assistant. Your job is to answer questions using the provided context which includes:
1. The user's personal documents and notes
2. The user's current asset portfolio from the database

CRITICAL INSTRUCTIONS:
1. Read the context carefully - it contains the user's personal notes AND their actual portfolio holdings
2. Extract and quote relevant information directly from the context
3. If the context contains the answer, provide it clearly and cite the source
4. If you're answering about specific assets, use the PORTFOLIO DATA for accurate holdings info
5. If you're answering about notes/strategies, use the DOCUMENT EXCERPTS
6. If the context does NOT contain the answer, say "I couldn't find that information."
7. Be specific and quote exact numbers, dates, and facts from the context

Example:
Context includes portfolio with AAPL: 100 shares at $150
Question: "How many AAPL shares do I own?"
Answer: "According to your portfolio, you own 100 shares of AAPL purchased at $150 per share."

Now answer the user's question using the provided context."""


async def execute_rag_query(
    query: str,
    user_id: str
) -> Dict[str, Any]:
    """Execute RAG query to answer document-based questions."""
    
    print(f"[RAG Pipeline] Query: {query}")
    print(f"[RAG Pipeline] User: {user_id}")
    
    # Fetch user assets from database
    user_assets = await _fetch_user_assets(user_id)
    asset_context = _format_asset_context(user_assets)
    
    print(f"[RAG Pipeline] Found {len(user_assets)} assets for user")
    
    if not is_available():
        # Still return asset info even if Pinecone unavailable
        if user_assets:
            return await _answer_with_assets_only(query, asset_context, user_assets)
        return {
            "success": False,
            "text": "Document search is not available. Please check Pinecone configuration.",
            "data": {},
            "sources": []
        }
    
    # Retrieve relevant documents
    matches = retrieve(query, user_id, top_k=10)
    print(f"[RAG Pipeline] Retrieved {len(matches)} document matches")
    
    # Format context for LLM
    doc_context = format_context(matches) if matches else ""
    sources = get_sources(matches) if matches else []
    
    # Add database source if assets found
    if user_assets:
        sources.append({
            "source": "Portfolio Database",
            "type": "database"
        })
    
    # Combine document context with asset context
    full_context = _build_full_context(asset_context, doc_context)
    
    print(f"[RAG Pipeline] Full context length: {len(full_context)} chars")
    
    if not full_context.strip():
        return {
            "success": True,
            "text": "I don't have any documents or portfolio data to search. Please upload some documents or add assets first.",
            "data": {},
            "sources": []
        }
    
    if not groq_client.is_available():
        return {
            "success": True,
            "text": f"Found relevant information:\n\n{full_context[:1000]}",
            "data": {"raw_context": full_context, "assets": user_assets},
            "sources": sources
        }
    
    # Generate answer using LLM
    try:
        user_message = f"""Here is the context:

{full_context}

---

Based on the above context (portfolio data + documents), answer this question: {query}

Remember: Extract the answer directly from the context. Be specific with numbers and dates."""

        messages = [
            {"role": "system", "content": RAG_SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ]
        
        response = groq_client.chat_completion(
            messages=messages,
            temperature=0.1,
            max_tokens=500
        )
        
        print(f"[RAG Pipeline] LLM Response: {response[:200]}...")
        
        return {
            "success": True,
            "text": response.strip(),
            "data": {
                "context_used": len(matches),
                "assets_used": len(user_assets),
                "user_portfolio": user_assets
            },
            "sources": sources
        }
    
    except Exception as e:
        print(f"[RAG Pipeline] LLM error: {e}")
        return {
            "success": False,
            "text": f"Error generating answer: {str(e)}",
            "data": {},
            "sources": sources
        }


async def _fetch_user_assets(user_id: str) -> List[Dict[str, Any]]:
    """Fetch user's assets from Supabase."""
    if not supabase:
        return []
    
    try:
        response = supabase.table("assets").select("*").eq("user_id", user_id).execute()
        return response.data or []
    except Exception as e:
        print(f"[RAG Pipeline] Error fetching assets: {e}")
        return []


def _format_asset_context(assets: List[Dict[str, Any]]) -> str:
    """Format user assets as context for the LLM."""
    if not assets:
        return ""
    
    lines = ["## USER'S PORTFOLIO (from database):\n"]
    
    for asset in assets:
        lines.append(f"- **{asset.get('symbol')}**: {asset.get('quantity')} shares")
        lines.append(f"  - Average Buy Price: ${asset.get('avg_buy_price', 'N/A')}")
        lines.append(f"  - Purchase Date: {asset.get('purchase_date', 'N/A')}")
        lines.append(f"  - Portfolio: {asset.get('portfolio_name', 'Default')}")
        lines.append(f"  - Broker: {asset.get('broker', 'N/A')}")
        lines.append(f"  - Type: {asset.get('investment_type', 'Stock')}")
        lines.append("")
    
    return "\n".join(lines)


def _build_full_context(asset_context: str, doc_context: str) -> str:
    """Combine asset and document context."""
    parts = []
    
    if asset_context:
        parts.append(asset_context)
    
    if doc_context:
        parts.append("## USER'S DOCUMENTS:\n")
        parts.append(doc_context)
    
    return "\n\n".join(parts)


async def _answer_with_assets_only(query: str, asset_context: str, assets: List[Dict]) -> Dict[str, Any]:
    """Answer using only asset data when documents unavailable."""
    if not groq_client.is_available():
        return {
            "success": True,
            "text": f"Here's your portfolio information:\n\n{asset_context}",
            "data": {"user_portfolio": assets},
            "sources": [{"source": "Portfolio Database", "type": "database"}]
        }
    
    try:
        messages = [
            {"role": "system", "content": "You are a helpful portfolio assistant. Answer questions about the user's portfolio."},
            {"role": "user", "content": f"Portfolio:\n{asset_context}\n\nQuestion: {query}"}
        ]
        
        response = groq_client.chat_completion(messages=messages, temperature=0.1, max_tokens=300)
        
        return {
            "success": True,
            "text": response.strip(),
            "data": {"user_portfolio": assets},
            "sources": [{"source": "Portfolio Database", "type": "database"}]
        }
    except:
        return {
            "success": True,
            "text": f"Here's your portfolio information:\n\n{asset_context}",
            "data": {"user_portfolio": assets},
            "sources": [{"source": "Portfolio Database", "type": "database"}]
        }

