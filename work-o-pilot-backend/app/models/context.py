"""
Conversation Context Manager
Handles context persistence and updates for multi-turn conversations
"""
from typing import Optional, List
from uuid import UUID
import json

from app.models.schemas import ConversationContext, TimeRange, RouterAIOutput
from app.services.supabase_client import supabase


async def get_context(conversation_id: UUID) -> ConversationContext:
    """
    Retrieve context for a conversation.
    
    Args:
        conversation_id: Conversation UUID
    
    Returns:
        ConversationContext object (empty if not found)
    """
    if not supabase:
        return ConversationContext()
    
    try:
        response = supabase.table("conversation_context").select("context").eq(
            "conversation_id", str(conversation_id)
        ).execute()
        
        if response.data and len(response.data) > 0:
            context_data = response.data[0].get("context", {})
            return ConversationContext(**context_data)
        
        return ConversationContext()
    
    except Exception as e:
        print(f"Error getting context: {e}")
        return ConversationContext()


async def save_context(conversation_id: UUID, context: ConversationContext) -> bool:
    """
    Save/update context for a conversation.
    
    Args:
        conversation_id: Conversation UUID
        context: ConversationContext to save
    
    Returns:
        True if successful
    """
    if not supabase:
        return False
    
    try:
        # Upsert context
        context_data = context.model_dump()
        
        # Convert TimeRange to dict if present
        if context_data.get("active_time_range"):
            context_data["active_time_range"] = context.active_time_range.model_dump() if context.active_time_range else None
        
        supabase.table("conversation_context").upsert({
            "conversation_id": str(conversation_id),
            "context": context_data
        }, on_conflict="conversation_id").execute()
        
        return True
    
    except Exception as e:
        print(f"Error saving context: {e}")
        return False


def update_context_from_result(
    context: ConversationContext,
    router_output: RouterAIOutput,
    result_data: dict
) -> ConversationContext:
    """
    Update context based on completed operation.
    
    Args:
        context: Current context
        router_output: Router AI output
        result_data: Analytics result data
    
    Returns:
        Updated ConversationContext
    """
    # Update active assets
    if router_output.entities.assets:
        context.active_assets = router_output.entities.assets
        
        # Add to history (unique)
        for asset in router_output.entities.assets:
            if asset not in context.mentioned_assets_history and asset != "__ALL__":
                context.mentioned_assets_history.append(asset)
    
    # Update time range
    context.active_time_range = router_output.entities.time_range
    
    # Update last operation
    context.last_operation = router_output.intent.task
    
    # Store last results (summary only, not full data)
    context.last_results = {
        "task": router_output.intent.task,
        "assets": router_output.entities.assets,
        "success": result_data.get("success", False)
    }
    
    return context


def resolve_reference(
    reference: str,
    context: ConversationContext
) -> Optional[List[str]]:
    """
    Resolve reference like "that stock", "the previous one" using context.
    
    Args:
        reference: Reference string from Router AI
        context: Current conversation context
    
    Returns:
        List of resolved asset symbols or None
    """
    if not reference:
        return None
    
    reference_lower = reference.lower()
    
    # "that stock", "that one", "it"
    if any(r in reference_lower for r in ["that", "it", "this", "the same"]):
        if context.active_assets:
            return context.active_assets
    
    # "the worst one", "the best one", "top performer"
    if "worst" in reference_lower or "bottom" in reference_lower:
        # Look in last results if it was a ranking
        if context.last_results.get("task") == "rank":
            return context.active_assets[:1] if context.active_assets else None
    
    if "best" in reference_lower or "top" in reference_lower:
        if context.last_results.get("task") == "rank":
            return context.active_assets[:1] if context.active_assets else None
    
    # Return active assets as fallback
    return context.active_assets if context.active_assets else None


async def create_conversation(user_id: str) -> Optional[UUID]:
    """
    Create a new conversation for user.
    
    Args:
        user_id: User UUID string
    
    Returns:
        New conversation UUID or None
    """
    if not supabase:
        return None
    
    try:
        response = supabase.table("conversations").insert({
            "user_id": user_id
        }).execute()
        
        if response.data:
            return UUID(response.data[0]["id"])
        return None
    
    except Exception as e:
        print(f"Error creating conversation: {e}")
        return None


async def save_message(
    conversation_id: UUID,
    role: str,
    content: str,
    metadata: dict = None
) -> Optional[UUID]:
    """
    Save a message to conversation history.
    
    Args:
        conversation_id: Conversation UUID
        role: "user" or "assistant"
        content: Message content
        metadata: Optional metadata dict
    
    Returns:
        Message UUID or None
    """
    if not supabase:
        return None
    
    try:
        response = supabase.table("messages").insert({
            "conversation_id": str(conversation_id),
            "role": role,
            "content": content,
            "metadata": metadata or {}
        }).execute()
        
        if response.data:
            return UUID(response.data[0]["id"])
        return None
    
    except Exception as e:
        print(f"Error saving message: {e}")
        return None
