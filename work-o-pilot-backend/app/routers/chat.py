"""
Chat Router
Main endpoint for the Stock Analytics AI Copilot
"""
from fastapi import APIRouter, HTTPException, status
from uuid import UUID
from typing import Optional

from app.models.schemas import ChatRequest, ChatResponse, ChatResponseData, VisualizationData, DataAccessed
from app.models.context import (
    get_context, save_context, update_context_from_result,
    create_conversation, save_message, resolve_reference
)
from app.services.router_ai import classify_intent, validate_router_output
from app.services.explanation_ai import generate_explanation, get_follow_up_question, extract_follow_up_from_response
from app.pipelines.dispatcher import dispatch
from app.pipelines.analytics.executor import get_user_tickers
from app.core.config import settings

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint for the Stock Analytics AI Copilot.
    
    Receives user query, classifies intent, executes appropriate pipeline,
    and returns response with explanation.
    """
    user_id = str(request.user_id)
    conversation_id = request.conversation_id
    user_query = request.user_query
    
    # Create new conversation if needed
    if not conversation_id:
        conversation_id = await create_conversation(user_id)
        if not conversation_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create conversation"
            )
    
    # Save user message
    await save_message(conversation_id, "user", user_query)
    
    # Get user's tickers for context
    user_tickers = get_user_tickers(user_id)
    
    # Get conversation context
    context = await get_context(conversation_id)
    
    # Classify intent using Router AI
    router_output = await classify_intent(user_query, user_tickers)
    
    # Validate and potentially correct Router AI output
    router_output = validate_router_output(router_output, user_tickers)
    
    # Resolve any references using context
    if router_output.entities.reference:
        resolved = resolve_reference(router_output.entities.reference, context)
        if resolved:
            router_output.entities.assets = resolved
    
    # Handle clarification needed
    if router_output.confidence.needs_clarification:
        clarification_text = router_output.confidence.clarification_prompt or "Could you please clarify your question?"
        
        # Save assistant response
        message_id = await save_message(
            conversation_id, "assistant", clarification_text,
            {"type": "clarification"}
        )
        
        return ChatResponse(
            conversation_id=conversation_id,
            message_id=message_id or UUID("00000000-0000-0000-0000-000000000000"),
            response=ChatResponseData(
                text=clarification_text,
                data={},
                visualization=None
            ),
            sources=[]
        )
    
    # Dispatch to appropriate pipeline
    result = await dispatch(router_output, user_id, user_query)
    
    # Generate explanation for analytics, use direct text for RAG
    follow_up = None
    if result.get("pipeline") == "rag":
        # For RAG, use the text directly from the RAG pipeline
        explanation = result.get("text", "")
        # Extract any follow-up from RAG response
        explanation, follow_up = extract_follow_up_from_response(explanation)
    else:
        # For analytics/forecasting, generate explanation
        raw_explanation = await generate_explanation(
            task=result.get("task", router_output.intent.task),
            data=result.get("data", {}),
            user_query=user_query,
            success=result.get("success", False)
        )
        # Extract AI-generated follow-up from response
        explanation, follow_up = extract_follow_up_from_response(raw_explanation)
    
    # Fallback to random follow-up if AI didn't generate one
    if not follow_up:
        task = result.get("task", router_output.intent.task)
        follow_up = get_follow_up_question(task)
    
    # Update context
    context = update_context_from_result(context, router_output, result)
    await save_context(conversation_id, context)
    
    # Prepare visualization data
    visualization = None
    if result.get("visualization"):
        visualization = VisualizationData(
            type=result["visualization"].get("type", "none"),
            chart_data=result["visualization"].get("chart_data", {}),
            image_base64=result["visualization"].get("image_base64")
        )
    
    # Prepare response text
    response_text = explanation
    if not result.get("success") and result.get("text"):
        response_text = result.get("text")
    
    # Save assistant response
    message_id = await save_message(
        conversation_id, "assistant", response_text,
        {
            "task": result.get("task"),
            "pipeline": result.get("pipeline"),
            "has_visualization": visualization is not None
        }
    )
    
    # Build data_accessed info
    data_accessed = None
    if result.get("success"):
        symbols = []
        records = 0
        time_range_str = None
        
        # Extract symbols from various result types
        data = result.get("data", {})
        if "metadata" in data:  # Forecasting
            symbols = [data["metadata"].get("entity", "")]
            records = data["metadata"].get("historical_records", 0)
            time_range_str = f"{data['metadata'].get('horizon_days', 30)} days forecast"
        elif "trends" in data:
            symbols = list(data["trends"].keys())
        elif "positions" in data:
            symbols = list(data["positions"].keys())
        elif "allocation" in data:
            symbols = [a["symbol"] for a in data["allocation"].get("allocations", [])]
        elif "rankings" in data:
            symbols = [r["symbol"] for r in data["rankings"].get("rankings", [])]
        
        if symbols:
            data_accessed = DataAccessed(
                symbols=[s for s in symbols if s],
                time_range=time_range_str,
                data_source="Yahoo Finance",
                records_fetched=records
            )
    
    return ChatResponse(
        conversation_id=conversation_id,
        message_id=message_id or UUID("00000000-0000-0000-0000-000000000000"),
        response=ChatResponseData(
            text=response_text,
            data=result.get("data", {}),
            visualization=visualization,
            follow_up_question=follow_up
        ),
        sources=result.get("sources", []),
        data_accessed=data_accessed
    )


@router.get("/history/{conversation_id}")
async def get_chat_history(conversation_id: UUID):
    """
    Get chat history for a conversation.
    """
    from app.services.supabase_client import supabase
    
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not available"
        )
    
    try:
        response = supabase.table("messages").select("*").eq(
            "conversation_id", str(conversation_id)
        ).order("created_at").execute()
        
        return {"conversation_id": conversation_id, "messages": response.data}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/conversations/{user_id}")
async def get_user_conversations(user_id: UUID):
    """
    Get all conversations for a user.
    """
    from app.services.supabase_client import supabase
    
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not available"
        )
    
    try:
        response = supabase.table("conversations").select("*").eq(
            "user_id", str(user_id)
        ).order("updated_at", desc=True).execute()
        
        return {"user_id": user_id, "conversations": response.data}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
