"""
Pipeline Dispatcher
Routes requests to appropriate pipeline (analytics or rag)
"""
from typing import Dict, Any
from uuid import UUID

from app.models.schemas import RouterAIOutput, AnalyticsResult, ChatResponseData, VisualizationData
from app.pipelines.analytics.executor import execute_analytics


async def dispatch(
    router_output: RouterAIOutput,
    user_id: str,
    user_query: str = ""
) -> Dict[str, Any]:
    """
    Dispatch to appropriate pipeline based on Router AI output.
    
    Args:
        router_output: Parsed Router AI output
        user_id: User UUID string
        user_query: Original user query (needed for RAG)
    
    Returns:
        Dict with pipeline results
    """
    pipeline = router_output.intent.pipeline
    
    # Check if clarification is needed
    if router_output.confidence.needs_clarification:
        return {
            "pipeline": "clarification",
            "success": False,
            "text": router_output.confidence.clarification_prompt or "Could you please clarify your question?",
            "data": {},
            "visualization": None
        }
    
    # Route to appropriate pipeline
    if pipeline == "analytics":
        result = await execute_analytics(router_output, user_id)
        return _format_analytics_result(result)
    
    elif pipeline == "rag":
        return await _execute_rag(router_output, user_id, user_query)
        
    elif pipeline == "forecasting":
        return await _execute_forecasting(router_output, user_id)
    
    else:
        return {
            "pipeline": pipeline,
            "success": False,
            "text": "Unknown pipeline type.",
            "data": {},
            "visualization": None
        }


from app.services.chart_generator import generate_chart

def _format_analytics_result(result: AnalyticsResult) -> Dict[str, Any]:
    """
    Format AnalyticsResult for response.
    """
    visualization = None
    if result.chart_data:
        vis_type = result.chart_data.get("type", "none")
        
        # Generate static image
        image_base64 = None
        if vis_type != "none":
            # Pass the raw data relevant to the chart, not just the chart_data metadata
            # The executor puts the actual data in result.data
            image_base64 = generate_chart(vis_type, result.data)
            
        visualization = {
            "type": vis_type,
            "chart_data": result.chart_data,
            "image_base64": image_base64
        }
    
    # Generate sources based on the data
    sources = []
    if result.success:
        # Extract symbols from result data
        symbols = []
        if "trends" in result.data:
            symbols = list(result.data["trends"].keys())
        elif "positions" in result.data:
            symbols = list(result.data["positions"].keys())
        elif "allocation" in result.data:
            symbols = [a["symbol"] for a in result.data["allocation"].get("allocations", [])]
        elif "rankings" in result.data:
            symbols = [r["symbol"] for r in result.data["rankings"].get("rankings", [])]
        elif "comparison" in result.data:
            symbols = [a["symbol"] for a in result.data["comparison"].get("assets", [])]
        elif "volatilities" in result.data:
            symbols = list(result.data["volatilities"].keys())
        elif "drawdowns" in result.data:
            symbols = list(result.data["drawdowns"].keys())
        
        # Add yfinance source for each symbol
        for symbol in symbols:
            sources.append({
                "name": f"Yahoo Finance - {symbol}",
                "url": f"https://finance.yahoo.com/quote/{symbol}",
                "type": "market_data"
            })
    
    return {
        "pipeline": "analytics",
        "success": result.success,
        "task": result.task,
        "text": result.error if not result.success else "",
        "data": result.data,
        "visualization": visualization,
        "sources": sources
    }


async def _execute_rag(
    router_output: RouterAIOutput,
    user_id: str,
    user_query: str
) -> Dict[str, Any]:
    """
    Execute RAG pipeline for document-based questions.
    """
    from app.pipelines.rag.pipeline import execute_rag_query
    
    result = await execute_rag_query(user_query, user_id)
    
    return {
        "pipeline": "rag",
        "success": result.get("success", False),
        "text": result.get("text", ""),
        "data": result.get("data", {}),
        "visualization": None,
        "sources": result.get("sources", [])
    }


async def _execute_forecasting(
    router_output: RouterAIOutput,
    user_id: str
) -> Dict[str, Any]:
    """
    Execute Forecasting pipeline.
    """
    from app.pipelines.forecasting.executor import execute_forecast
    
    result = await execute_forecast(router_output, user_id)
    
    # Extract symbol from metadata for sources
    symbol = result.get("data", {}).get("metadata", {}).get("entity", "")
    
    # Build sources with proper URLs
    sources = []
    if symbol:
        sources.append({
            "name": f"Yahoo Finance - {symbol}",
            "url": f"https://finance.yahoo.com/quote/{symbol}",
            "type": "market_data"
        })
    sources.append({
        "name": "Meta Prophet",
        "url": "https://facebook.github.io/prophet/",
        "type": "model"
    })
    
    return {
        "pipeline": "forecasting",
        "task": "forecast",  # Add task for explanation AI
        "success": result.get("success", False),
        "text": result.get("text", ""),
        "data": result.get("data", {}),
        "visualization": result.get("visualization"),
        "sources": sources
    }

