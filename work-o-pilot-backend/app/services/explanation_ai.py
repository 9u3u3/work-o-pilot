"""
Explanation AI Service
Generates human-readable explanations of analytics results
"""
from typing import Dict, Any

from app.services.groq_client import groq_client
from app.models.schemas import RouterAIOutput


EXPLANATION_SYSTEM_PROMPT = """You are a helpful financial assistant explaining stock analytics results.

Your job:
1. Take computed analytics data
2. Explain it in clear, conversational language using **markdown formatting**
3. Highlight key insights
4. Reference the visualization if one is provided
5. ALWAYS end with a contextual follow-up question

Markdown formatting rules:
- Use **bold** for important numbers, percentages, and key terms
- Use bullet points for multiple items
- Use > blockquotes for key insights
- Keep responses concise (3-5 sentences max)
- If there's chart data, mention it: "See the chart below for visual details."

IMPORTANT - Follow-up question:
- At the END of your response, ALWAYS add a line break and ask ONE relevant follow-up question
- The question should be related to the data shown
- Examples: "Would you like to see the revenue breakdown?", "Should I compare this with last month?", "Want to see a forecast for this stock?"
- Format: Put the follow-up on its own line starting with "📊 "

Rules:
- Do NOT perform any calculations
- Do NOT make up numbers - use ONLY the provided data
- Do NOT give financial advice
- Be factual and neutral
- Use the user's perspective ("Your AAPL position...")
- Format numbers nicely (e.g., "$1,234.56", "12.5%")

Respond with the markdown explanation followed by the follow-up question."""


FOLLOW_UP_QUESTIONS = {
    "trend": [
        "Would you like to see a longer time range?",
        "Should I compare this with another stock?",
        "Want to see the volatility for this period?"
    ],
    "allocation": [
        "Would you like to see your P&L breakdown?",
        "Should I show you the top performers?",
        "Want to see how this compares to last month?"
    ],
    "pnl": [
        "Would you like a trend analysis for any position?",
        "Should I show the allocation breakdown?",
        "Want to see the volatility of your positions?"
    ],
    "rank": [
        "Would you like more details on any of these?",
        "Should I show a comparison chart?",
        "Want to see a trend for the top performer?"
    ],
    "forecast": [
        "Would you like to forecast for a different period?",
        "Should I forecast another stock?",
        "Want to see the historical trend as well?"
    ],
    "comparison": [
        "Would you like to see the forecast for any of these?",
        "Should I add more stocks to compare?",
        "Want to see the volatility comparison?"
    ],
    "volatility": [
        "Would you like to see the price trend?",
        "Should I compare volatility with other stocks?",
        "Want a forecast for this stock?"
    ],
    "general_question": [
        "Is there anything else you'd like to know?",
        "Would you like me to analyze any specific stock?",
        "Should I show you your portfolio overview?"
    ]
}


def get_follow_up_question(task: str) -> str:
    """Get a relevant follow-up question based on the task type (fallback)."""
    import random
    questions = FOLLOW_UP_QUESTIONS.get(task, FOLLOW_UP_QUESTIONS["general_question"])
    return random.choice(questions)


def extract_follow_up_from_response(response: str) -> tuple:
    """
    Extract the follow-up question from AI response if present.
    Returns (main_response, follow_up_question)
    """
    # Look for 📊 prefix which indicates follow-up
    if "📊" in response:
        parts = response.rsplit("📊", 1)
        main_response = parts[0].strip()
        follow_up = parts[1].strip() if len(parts) > 1 else None
        return main_response, follow_up
    
    # Alternative: look for last line starting with question words
    lines = response.strip().split("\n")
    if len(lines) > 1:
        last_line = lines[-1].strip()
        question_starters = ["Would you", "Should I", "Want to", "Do you", "Can I", "Shall I"]
        if any(last_line.startswith(q) for q in question_starters) and last_line.endswith("?"):
            main_response = "\n".join(lines[:-1]).strip()
            return main_response, last_line
    
    return response, None


def create_explanation_prompt(
    task: str,
    data: Dict[str, Any],
    user_query: str
) -> str:
    """
    Create prompt for Explanation AI.
    
    Args:
        task: Analytics task type
        data: Analytics result data
        user_query: Original user query
    
    Returns:
        Formatted prompt string
    """
    return f"""Task: {task}
User Question: "{user_query}"

Analytics Results:
{format_data_for_explanation(data)}

Provide a clear, conversational explanation of these results."""


def format_data_for_explanation(data: Dict[str, Any]) -> str:
    """
    Format analytics data for LLM consumption.
    
    Args:
        data: Analytics result data
    
    Returns:
        Formatted string representation
    """
    import json
    return json.dumps(data, indent=2, default=str)


async def generate_explanation(
    task: str,
    data: Dict[str, Any],
    user_query: str,
    success: bool = True
) -> str:
    """
    Generate human-readable explanation of analytics results.
    
    Args:
        task: Analytics task type
        data: Analytics result data
        user_query: Original user query
        success: Whether analytics was successful
    
    Returns:
        Human-readable explanation string
    """
    if not success:
        return data.get("error", "I wasn't able to complete your request.")
    
    if not groq_client.is_available():
        return generate_fallback_explanation(task, data)
    
    messages = [
        {"role": "system", "content": EXPLANATION_SYSTEM_PROMPT},
        {"role": "user", "content": create_explanation_prompt(task, data, user_query)}
    ]
    
    try:
        response = groq_client.chat_completion(
            messages=messages,
            temperature=0.3,
            max_tokens=500
        )
        return response.strip()
    
    except Exception as e:
        print(f"Explanation AI error: {e}")
        return generate_fallback_explanation(task, data)


def generate_fallback_explanation(task: str, data: Dict[str, Any]) -> str:
    """
    Generate basic explanation when AI is unavailable.
    
    Args:
        task: Analytics task type
        data: Analytics result data
    
    Returns:
        Basic explanation string
    """
    if task == "trend":
        trends = data.get("trends", {})
        if trends:
            first_symbol = list(trends.keys())[0]
            trend = trends[first_symbol]
            direction = trend.get("trend_direction", "flat")
            change = trend.get("change_percent", 0)
            return f"{first_symbol} has shown a {direction} trend with a {change:.2f}% change."
    
    elif task == "pnl":
        total = data.get("total", {})
        if total:
            pnl = total.get("total_unrealized_pnl", 0)
            pnl_pct = total.get("total_pnl_percent", 0)
            direction = "up" if pnl > 0 else "down"
            return f"Your portfolio is {direction} ${abs(pnl):.2f} ({pnl_pct:.2f}%)."
    
    elif task == "rank":
        rankings = data.get("rankings", {}).get("rankings", [])
        if rankings:
            top = rankings[0]
            return f"{top.get('symbol')} is your {'top' if data.get('rankings', {}).get('direction') == 'top' else 'bottom'} performer with {top.get('change_percent', 0):.2f}% change."
    
    elif task == "allocation":
        alloc = data.get("allocation", {})
        total = alloc.get("total_value", 0)
        positions = len(alloc.get("allocations", []))
        return f"Your portfolio has {positions} positions worth ${total:.2f} total."
    
    elif task == "comparison":
        comparison = data.get("comparison", {})
        assets = comparison.get("assets", [])
        if len(assets) >= 2:
            best = max(assets, key=lambda x: x.get("change_percent", 0))
            return f"Among your compared stocks, {best.get('symbol')} performed best with {best.get('change_percent', 0):.2f}% change."
            
    elif task == "forecast":
        metrics = data.get("metrics", {})
        metadata = data.get("metadata", {})
        forecast_list = data.get("forecast", [])
        
        entity = metadata.get("entity", "Stock")
        trend = metrics.get("trend", "flat")
        growth = metrics.get("avg_growth_rate", 0) * 100
        volatility = metrics.get("volatility", "unknown")
        confidence = metrics.get("confidence", 0) * 100
        horizon_days = metadata.get("horizon_days", 30)
        
        # Get first and last forecast values
        start_price = forecast_list[0]["yhat"] if forecast_list else 0
        end_price = forecast_list[-1]["yhat"] if forecast_list else 0
        start_date = forecast_list[0]["ds"] if forecast_list else ""
        end_date = forecast_list[-1]["ds"] if forecast_list else ""
        
        price_change = end_price - start_price
        price_change_pct = (price_change / start_price * 100) if start_price else 0
        
        summary = f"""## **{entity} {horizon_days}-Day Forecast**

**Trend Direction:** {trend.upper()}
**Average Daily Growth:** {growth:.2f}%
**Volatility:** {volatility.upper()}
**Model Confidence:** {confidence:.1f}%

### Price Prediction
- **Start ({start_date}):** ${start_price:.2f}
- **End ({end_date}):** ${end_price:.2f}
- **Predicted Change:** ${price_change:.2f} ({price_change_pct:+.2f}%)

> See the chart below for the full forecast with confidence intervals."""
        
        return summary
    
    return "Here are your analytics results."
