"""
Router AI Service
Classifies user intent and extracts entities using GROQ LLM
"""
from typing import List, Optional
import json

from app.services.groq_client import groq_client
from app.models.schemas import RouterAIOutput, Intent, Entities, Operations, Visualization, Confidence, TimeRange


ROUTER_SYSTEM_PROMPT = """You are an intent classifier for a stock analytics app. Classify the user's query.

IMPORTANT: Output ONLY valid JSON. Do NOT include explanations or markdown.

PIPELINE VALUES (choose exactly one):
- "analytics" - for LIVE stock data like current prices, charts, P&L, trends, rankings
- "rag" - for questions about user's PERSONAL NOTES/DOCUMENTS, investment strategy, plans, written info
- "forecasting" - for FUTURE predictions, price targets, "forecast", "predict"
- "clarification" - if query is unclear

WHEN TO USE FORECASTING (pipeline = "forecasting"):
- "Forecast AAPL for next month"
- "Predict Tesla price"
- "What will be the price of NVDA?"
- Future tense questions about price

WHEN TO USE RAG (pipeline = "rag"):
- Questions about "my notes", "my documents", "according to my notes"
- Questions about personal strategy, cost basis from notes, investment philosophy
- Questions about what user WROTE or DOCUMENTED
- Any question that requires searching the user's uploaded documents

WHEN TO USE ANALYTICS (pipeline = "analytics"):
- Current stock prices, trends, performance
- Portfolio allocation (actual holdings), P&L
- Rankings, comparisons of actual stock performance

TASK VALUES (choose exactly one):
- "allocation" - portfolio breakdown/allocation questions
- "pnl" - profit/loss, unrealized gains
- "trend" - price trend over time
- "rank" - top/bottom performers
- "change" - percentage/price change
- "comparison" - compare multiple stocks
- "volatility" - volatility analysis
- "drawdown" - max drawdown
- "forecast" - price prediction
- "general_question" - for RAG/document questions

Example for "What is my portfolio allocation?" (ANALYTICS - actual holdings):
{"intent":{"pipeline":"analytics","task":"allocation"},"entities":{"assets":["__ALL__"],"metrics":["price"],"time_range":{"type":"relative","value":1,"unit":"months","start_date":null,"end_date":null},"reference":null},"operations":{"analysis_type":"allocation","direction":null,"rank_n":null,"aggregation":null},"visualization":{"required":true,"type":"pie_chart"},"confidence":{"needs_clarification":false,"missing_fields":[],"clarification_prompt":null}}

Example for "What is my cost basis according to my notes?" (RAG - document search):
{"intent":{"pipeline":"rag","task":"general_question"},"entities":{"assets":[],"metrics":[],"time_range":{"type":"relative","value":1,"unit":"months","start_date":null,"end_date":null},"reference":null},"operations":{"analysis_type":"trend","direction":null,"rank_n":null,"aggregation":null},"visualization":{"required":false,"type":"none"},"confidence":{"needs_clarification":false,"missing_fields":[],"clarification_prompt":null}}

Example for "What did I write about my investment strategy?" (RAG):
{"intent":{"pipeline":"rag","task":"general_question"},"entities":{"assets":[],"metrics":[],"time_range":{"type":"relative","value":1,"unit":"months","start_date":null,"end_date":null},"reference":null},"operations":{"analysis_type":"trend","direction":null,"rank_n":null,"aggregation":null},"visualization":{"required":false,"type":"none"},"confidence":{"needs_clarification":false,"missing_fields":[],"clarification_prompt":null}}

Example for "Forecast AAPL for 30 days" (FORECASTING):
{"intent":{"pipeline":"forecasting","task":"forecast"},"entities":{"assets":["AAPL"],"metrics":["price"],"time_range":{"type":"relative","value":30,"unit":"days","start_date":null,"end_date":null},"reference":null},"operations":{"analysis_type":"trend","direction":null,"rank_n":null,"aggregation":null},"visualization":{"required":true,"type":"line_chart"},"confidence":{"needs_clarification":false,"missing_fields":[],"clarification_prompt":null}}

Output ONLY the JSON object."""


def create_router_prompt(user_query: str, user_tickers: List[str]) -> str:
    """
    Create the user message for Router AI.
    
    Args:
        user_query: User's natural language query
        user_tickers: List of tickers the user owns
    
    Returns:
        Formatted prompt string
    """
    tickers_str = ", ".join(user_tickers) if user_tickers else "No stocks added yet"
    
    return f"""User Query: "{user_query}"

User's Portfolio Tickers: [{tickers_str}]

Classify this query and extract all relevant information."""


def parse_router_response(response: str) -> RouterAIOutput:
    """
    Parse and validate Router AI JSON response with robust error handling.
    """
    print(f"[Router AI] Raw response: {response[:500]}...")  # Log first 500 chars
    
    try:
        data = groq_client.parse_json_response(response)
        print(f"[Router AI] Parsed JSON: {data}")
        
        # Extract with safe defaults
        intent_data = data.get("intent", {})
        entities_data = data.get("entities", {})
        time_range_data = entities_data.get("time_range", {}) or {}
        operations_data = data.get("operations", {})
        visualization_data = data.get("visualization", {})
        confidence_data = data.get("confidence", {})
        
        # Build TimeRange with safe defaults for None values
        # Validate type - must be 'relative' or 'absolute'
        tr_type = time_range_data.get("type")
        if tr_type not in ("relative", "absolute"):
            tr_type = "relative"
        
        time_range = TimeRange(
            type=tr_type,
            value=time_range_data.get("value") or 1,
            unit=time_range_data.get("unit") or "months",
            start_date=time_range_data.get("start_date"),
            end_date=time_range_data.get("end_date")
        )
        
        # Build Intent with safe defaults
        intent = Intent(
            pipeline=intent_data.get("pipeline") or "analytics",
            task=intent_data.get("task") or "allocation"
        )
        
        # Build Entities
        entities = Entities(
            assets=entities_data.get("assets") or ["__ALL__"],
            metrics=entities_data.get("metrics") or ["price"],
            time_range=time_range,
            reference=entities_data.get("reference")
        )
        
        # Build Operations with safe defaults
        operations = Operations(
            analysis_type=operations_data.get("analysis_type") or "trend",
            direction=operations_data.get("direction"),
            rank_n=operations_data.get("rank_n"),
            aggregation=operations_data.get("aggregation")
        )
        
        # Build Visualization
        visualization = Visualization(
            required=visualization_data.get("required", True),
            type=visualization_data.get("type") or "table"
        )
        
        # Build Confidence
        confidence = Confidence(
            needs_clarification=confidence_data.get("needs_clarification", False),
            missing_fields=confidence_data.get("missing_fields") or [],
            clarification_prompt=confidence_data.get("clarification_prompt")
        )
        
        result = RouterAIOutput(
            intent=intent,
            entities=entities,
            operations=operations,
            visualization=visualization,
            confidence=confidence
        )
        
        print(f"[Router AI] Parsed successfully: pipeline={intent.pipeline}, task={intent.task}")
        return result
    
    except json.JSONDecodeError as e:
        print(f"[Router AI] JSON parse error: {e}")
        print(f"[Router AI] Response was: {response}")
        return RouterAIOutput(
            confidence=Confidence(
                needs_clarification=True,
                clarification_prompt="I couldn't understand your request. Could you please rephrase?"
            )
        )
    
    except Exception as e:
        print(f"[Router AI] Parse error: {e}")
        print(f"[Router AI] Response was: {response}")
        return RouterAIOutput(
            confidence=Confidence(
                needs_clarification=True,
                clarification_prompt="Something went wrong. Please try again."
            )
        )


async def classify_intent(
    user_query: str,
    user_tickers: List[str]
) -> RouterAIOutput:
    """
    Classify user intent using Router AI.
    
    Args:
        user_query: User's natural language query
        user_tickers: List of tickers the user owns
    
    Returns:
        RouterAIOutput with classified intent and extracted entities
    """
    if not groq_client.is_available():
        print("GROQ client not available")
        return RouterAIOutput(
            confidence=Confidence(
                needs_clarification=True,
                clarification_prompt="AI service is not available. Please check configuration."
            )
        )
    
    messages = [
        {"role": "system", "content": ROUTER_SYSTEM_PROMPT},
        {"role": "user", "content": create_router_prompt(user_query, user_tickers)}
    ]
    
    try:
        response = groq_client.chat_completion(
            messages=messages,
            temperature=0.0,
            response_format={"type": "json_object"}
        )
        
        return parse_router_response(response)
    
    except Exception as e:
        print(f"Router AI error: {e}")
        return RouterAIOutput(
            confidence=Confidence(
                needs_clarification=True,
                clarification_prompt="AI service encountered an error. Please try again."
            )
        )


def validate_router_output(
    output: RouterAIOutput,
    user_tickers: List[str]
) -> RouterAIOutput:
    """
    Post-validation of Router AI output.
    
    Args:
        output: RouterAIOutput from AI
        user_tickers: User's actual tickers
    
    Returns:
        Validated and potentially corrected RouterAIOutput
    """
    # If needs clarification, return as-is
    if output.confidence.needs_clarification:
        return output
    
    # Validate assets exist in portfolio (unless __ALL__)
    if output.entities.assets and "__ALL__" not in output.entities.assets:
        valid_assets = []
        invalid_assets = []
        
        for asset in output.entities.assets:
            if asset.upper() in [t.upper() for t in user_tickers]:
                valid_assets.append(asset.upper())
            else:
                invalid_assets.append(asset)
        
        if invalid_assets and not valid_assets:
            # No valid assets found
            output.confidence.needs_clarification = True
            output.confidence.clarification_prompt = f"I couldn't find {', '.join(invalid_assets)} in your portfolio. Your stocks are: {', '.join(user_tickers)}"
            output.confidence.missing_fields = ["assets"]
        elif valid_assets:
            output.entities.assets = valid_assets
    
    return output
