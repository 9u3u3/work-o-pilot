"""
Pydantic schemas for Stock Analytics AI Copilot
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Literal, Dict, Any
from datetime import datetime, date
from uuid import UUID


# ========================
# Router AI Output Schemas
# ========================

class TimeRange(BaseModel):
    type: Literal["relative", "absolute"] = "relative"
    value: Optional[int] = 1
    unit: Literal["days", "weeks", "months", "years"] = "months"
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class Entities(BaseModel):
    assets: List[str] = Field(default_factory=list)
    metrics: List[str] = Field(default_factory=lambda: ["price"])
    time_range: TimeRange = Field(default_factory=TimeRange)
    reference: Optional[str] = None


class Intent(BaseModel):
    pipeline: Literal["analytics", "rag", "clarification", "forecasting"] = "analytics"
    task: Literal[
        "trend", "rank", "change", "comparison", "pnl", 
        "volatility", "drawdown", "allocation", "general_question", "forecast"
    ] = "trend"


class Operations(BaseModel):
    analysis_type: Literal["trend", "rank", "change", "comparison", "pnl", "allocation", "volatility", "drawdown"] = "trend"
    direction: Optional[Literal["top", "bottom"]] = None
    rank_n: Optional[int] = None
    aggregation: Optional[Literal["daily", "weekly", "monthly"]] = None


class Visualization(BaseModel):
    required: bool = True
    type: Literal["line_chart", "bar_chart", "table", "pie_chart", "none"] = "line_chart"


class Confidence(BaseModel):
    needs_clarification: bool = False
    missing_fields: List[str] = Field(default_factory=list)
    clarification_prompt: Optional[str] = None


class RouterAIOutput(BaseModel):
    intent: Intent = Field(default_factory=Intent)
    entities: Entities = Field(default_factory=Entities)
    operations: Operations = Field(default_factory=Operations)
    visualization: Visualization = Field(default_factory=Visualization)
    confidence: Confidence = Field(default_factory=Confidence)


# ========================
# Chat Request/Response
# ========================

class ChatRequest(BaseModel):
    user_id: UUID
    conversation_id: Optional[UUID] = None
    user_query: str


class VisualizationData(BaseModel):
    type: str
    chart_data: Dict[str, Any] = Field(default_factory=dict)
    image_base64: Optional[str] = None


class DataAccessed(BaseModel):
    """Details about what data was accessed for the response"""
    symbols: List[str] = Field(default_factory=list)
    time_range: Optional[str] = None
    data_source: str = "Yahoo Finance"
    records_fetched: int = 0


class ChatResponseData(BaseModel):
    text: str
    data: dict = Field(default_factory=dict)
    visualization: Optional[VisualizationData] = None
    follow_up_question: Optional[str] = None


class ChatResponse(BaseModel):
    conversation_id: UUID
    message_id: UUID
    response: ChatResponseData
    sources: List[dict] = Field(default_factory=list)
    data_accessed: Optional[DataAccessed] = None



# ========================
# Analytics Results
# ========================

class TrendResult(BaseModel):
    symbol: str
    start_price: float
    end_price: float
    change_absolute: float
    change_percent: float
    trend_direction: Literal["up", "down", "flat"]
    data_points: List[dict] = Field(default_factory=list)


class PnLResult(BaseModel):
    symbol: str
    quantity: float
    avg_buy_price: float
    current_price: float
    cost_basis: float
    current_value: float
    unrealized_pnl: float
    pnl_percent: float


class RankResult(BaseModel):
    rankings: List[dict] = Field(default_factory=list)
    direction: str
    metric: str


class AnalyticsResult(BaseModel):
    task: str
    success: bool
    data: dict = Field(default_factory=dict)
    chart_data: Optional[dict] = None
    error: Optional[str] = None


# ========================
# Context Schema
# ========================

class ConversationContext(BaseModel):
    active_assets: List[str] = Field(default_factory=list)
    active_time_range: Optional[TimeRange] = None
    last_operation: Optional[str] = None
    last_results: dict = Field(default_factory=dict)
    mentioned_assets_history: List[str] = Field(default_factory=list)


# ========================
# Asset Schema (from DB)
# ========================

class Asset(BaseModel):
    id: UUID
    user_id: UUID
    symbol: str
    quantity: float
    avg_buy_price: float
    purchase_date: Optional[date] = None
    portfolio_name: Optional[str] = None
    currency: str = "USD"
    broker: Optional[str] = None
    investment_type: str = "Stock"
    exchange: Optional[str] = None
