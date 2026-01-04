"""
Analytics Pipeline Executor
Orchestrates analytics tasks based on Router AI output
"""
from typing import Dict, List, Optional, Tuple
from uuid import UUID

from app.models.schemas import (
    RouterAIOutput, AnalyticsResult, Asset, TimeRange,
    TrendResult, PnLResult, RankResult
)
from app.pipelines.analytics.market_data import (
    fetch_stock_data, fetch_multiple_stocks, 
    get_current_prices, get_current_price,
    normalize_symbol, get_asset_type, get_data_source_name
)
from app.pipelines.analytics.calculators import (
    calculate_trend, calculate_percentage_change, calculate_absolute_change,
    rank_by_performance, calculate_unrealized_pnl, calculate_total_pnl,
    calculate_volatility, calculate_drawdown, calculate_allocation,
    compare_assets, generate_chart_data
)
from app.services.supabase_client import supabase


def get_user_assets(user_id: str) -> List[Asset]:
    """
    Fetch user's assets from Supabase.
    
    Args:
        user_id: User UUID string
    
    Returns:
        List of Asset objects
    """
    if not supabase:
        return []
    
    try:
        response = supabase.table("assets").select("*").eq("user_id", user_id).execute()
        assets = []
        for row in response.data:
            assets.append(Asset(
                id=row["id"],
                user_id=row["user_id"],
                symbol=row["symbol"],
                quantity=row["quantity"],
                avg_buy_price=row["avg_buy_price"],
                purchase_date=row.get("purchase_date"),
                portfolio_name=row.get("portfolio_name"),
                currency=row.get("currency", "USD"),
                broker=row.get("broker"),
                investment_type=row.get("investment_type", "Stock"),
                exchange=row.get("exchange")
            ))
        return assets
    except Exception as e:
        print(f"Error fetching user assets: {e}")
        return []


def get_user_tickers(user_id: str) -> List[str]:
    """
    Get list of ticker symbols owned by user.
    
    Args:
        user_id: User UUID string
    
    Returns:
        List of ticker symbols
    """
    assets = get_user_assets(user_id)
    return list(set(asset.symbol for asset in assets))


def resolve_assets(
    requested_assets: List[str],
    user_assets: List[Asset],
    allow_external: bool = True
) -> Tuple[List[str], bool]:
    """
    Resolve requested assets, handling __ALL__ and validating against user's portfolio.
    Also handles external assets (like gold, bitcoin) that don't need to be in portfolio.
    
    Args:
        requested_assets: List from Router AI (may include "__ALL__")
        user_assets: User's actual assets
        allow_external: If True, allow assets not in portfolio (for market queries)
    
    Returns:
        Tuple of (resolved tickers, is_external_query)
    """
    user_tickers = [a.symbol.upper() for a in user_assets]
    
    if "__ALL__" in requested_assets or not requested_assets:
        return user_tickers, False
    
    # Normalize all requested assets
    normalized = []
    for ticker in requested_assets:
        normalized.append(normalize_symbol(ticker))
    
    # Check if any are in user's portfolio
    portfolio_assets = [t for t in normalized if t.upper() in user_tickers]
    
    # If we have portfolio matches, use those
    if portfolio_assets:
        return portfolio_assets, False
    
    # If allow_external and no portfolio matches, treat as external market query
    if allow_external and normalized:
        return normalized, True
    
    return [], False


async def execute_analytics(
    router_output: RouterAIOutput,
    user_id: str
) -> AnalyticsResult:
    """
    Execute analytics task based on Router AI output.
    
    Args:
        router_output: Parsed output from Router AI
        user_id: User UUID string
    
    Returns:
        AnalyticsResult with computed data
    """
    task = router_output.intent.task
    entities = router_output.entities
    operations = router_output.operations
    visualization = router_output.visualization
    
    # Get user's assets
    user_assets = get_user_assets(user_id)
    
    # Resolve which assets to analyze
    requested = entities.assets
    
    # Determine if this requires portfolio assets or allows external queries
    requires_portfolio = task in ["pnl", "allocation", "rank"]
    assets_to_analyze, is_external = resolve_assets(
        requested, 
        user_assets, 
        allow_external=not requires_portfolio
    )
    
    # For portfolio-required tasks, we need user assets
    if requires_portfolio and not user_assets:
        return AnalyticsResult(
            task=task,
            success=False,
            error="No assets found in your portfolio. Please add some assets first."
        )
    
    # For external queries without portfolio, just check if we have symbols
    if not assets_to_analyze and not is_external:
        return AnalyticsResult(
            task=task,
            success=False,
            error=f"Requested assets {requested} not found. Try using ticker symbols like AAPL, BTC, GOLD."
        )
    
    time_range = entities.time_range
    
    try:
        # Execute based on task type
        if task == "trend":
            return await _execute_trend(assets_to_analyze, time_range, visualization.type)
        
        elif task == "change":
            return await _execute_change(assets_to_analyze, time_range, visualization.type)
        
        elif task == "rank":
            direction = operations.direction or "top"
            rank_n = operations.rank_n or 5
            return await _execute_rank(user_assets, time_range, direction, rank_n, visualization.type)
        
        elif task == "pnl":
            return await _execute_pnl(user_assets, assets_to_analyze, visualization.type)
        
        elif task == "comparison":
            return await _execute_comparison(assets_to_analyze, time_range, visualization.type)
        
        elif task == "volatility":
            return await _execute_volatility(assets_to_analyze, time_range)
        
        elif task == "drawdown":
            return await _execute_drawdown(assets_to_analyze, time_range)
        
        elif task == "allocation":
            return await _execute_allocation(user_assets)
        
        else:
            return AnalyticsResult(
                task=task,
                success=False,
                error=f"Unknown analytics task: {task}"
            )
    
    except Exception as e:
        return AnalyticsResult(
            task=task,
            success=False,
            error=f"Analytics error: {str(e)}"
        )


async def _execute_trend(
    symbols: List[str],
    time_range: TimeRange,
    chart_type: str
) -> AnalyticsResult:
    """Execute trend analysis."""
    dfs = fetch_multiple_stocks(symbols, time_range)
    
    if not dfs:
        return AnalyticsResult(task="trend", success=False, error="Could not fetch market data.")
    
    trends = {}
    for symbol, df in dfs.items():
        trend = calculate_trend(df, symbol)
        trends[symbol] = trend.model_dump()
    
    chart_data = generate_chart_data(dfs, "line_chart")
    
    return AnalyticsResult(
        task="trend",
        success=True,
        data={"trends": trends},
        chart_data=chart_data
    )


async def _execute_change(
    symbols: List[str],
    time_range: TimeRange,
    chart_type: str
) -> AnalyticsResult:
    """Execute change calculation."""
    dfs = fetch_multiple_stocks(symbols, time_range)
    
    if not dfs:
        return AnalyticsResult(task="change", success=False, error="Could not fetch market data.")
    
    changes = {}
    for symbol, df in dfs.items():
        changes[symbol] = {
            "percent": calculate_percentage_change(df),
            "absolute": calculate_absolute_change(df)
        }
    
    chart_data = generate_chart_data(dfs, "bar_chart")
    
    return AnalyticsResult(
        task="change",
        success=True,
        data={"changes": changes},
        chart_data=chart_data
    )


async def _execute_rank(
    user_assets: List[Asset],
    time_range: TimeRange,
    direction: str,
    rank_n: int,
    chart_type: str
) -> AnalyticsResult:
    """Execute ranking analysis."""
    symbols = [a.symbol for a in user_assets]
    dfs = fetch_multiple_stocks(symbols, time_range)
    
    if not dfs:
        return AnalyticsResult(task="rank", success=False, error="Could not fetch market data.")
    
    rank_result = rank_by_performance(dfs, direction, rank_n)
    
    # Generate bar chart for rankings
    chart_data = {
        "type": "bar_chart",
        "labels": [r["symbol"] for r in rank_result.rankings],
        "values": [r["change_percent"] for r in rank_result.rankings]
    }
    
    return AnalyticsResult(
        task="rank",
        success=True,
        data={"rankings": rank_result.model_dump()},
        chart_data=chart_data
    )


async def _execute_pnl(
    user_assets: List[Asset],
    symbols: List[str],
    chart_type: str
) -> AnalyticsResult:
    """Execute P&L calculation."""
    # Filter assets to requested symbols
    relevant_assets = [a for a in user_assets if a.symbol.upper() in [s.upper() for s in symbols]]
    
    if not relevant_assets:
        return AnalyticsResult(task="pnl", success=False, error="No matching assets found.")
    
    # Get current prices
    current_prices = get_current_prices([a.symbol for a in relevant_assets])
    
    if not current_prices:
        return AnalyticsResult(task="pnl", success=False, error="Could not fetch current prices.")
    
    pnl_results = calculate_unrealized_pnl(relevant_assets, current_prices)
    total_pnl = calculate_total_pnl(pnl_results)
    
    # Convert to serializable format
    pnl_data = {symbol: result.model_dump() for symbol, result in pnl_results.items()}
    
    return AnalyticsResult(
        task="pnl",
        success=True,
        data={"positions": pnl_data, "total": total_pnl},
        chart_data={"type": "table", "data": pnl_data}
    )


async def _execute_comparison(
    symbols: List[str],
    time_range: TimeRange,
    chart_type: str
) -> AnalyticsResult:
    """Execute multi-asset comparison."""
    if len(symbols) < 2:
        return AnalyticsResult(task="comparison", success=False, error="Need at least 2 assets to compare.")
    
    dfs = fetch_multiple_stocks(symbols, time_range)
    
    if len(dfs) < 2:
        return AnalyticsResult(task="comparison", success=False, error="Could not fetch data for comparison.")
    
    comparison = compare_assets(dfs)
    chart_data = generate_chart_data(dfs, "line_chart")
    
    return AnalyticsResult(
        task="comparison",
        success=True,
        data={"comparison": comparison},
        chart_data=chart_data
    )


async def _execute_volatility(
    symbols: List[str],
    time_range: TimeRange
) -> AnalyticsResult:
    """Execute volatility calculation."""
    dfs = fetch_multiple_stocks(symbols, time_range)
    
    if not dfs:
        return AnalyticsResult(task="volatility", success=False, error="Could not fetch market data.")
    
    volatilities = {}
    for symbol, df in dfs.items():
        volatilities[symbol] = calculate_volatility(df)
    
    return AnalyticsResult(
        task="volatility",
        success=True,
        data={"volatilities": volatilities},
        chart_data={"type": "bar_chart", "labels": list(volatilities.keys()), "values": list(volatilities.values())}
    )


async def _execute_drawdown(
    symbols: List[str],
    time_range: TimeRange
) -> AnalyticsResult:
    """Execute drawdown calculation."""
    dfs = fetch_multiple_stocks(symbols, time_range)
    
    if not dfs:
        return AnalyticsResult(task="drawdown", success=False, error="Could not fetch market data.")
    
    drawdowns = {}
    for symbol, df in dfs.items():
        drawdowns[symbol] = calculate_drawdown(df)
    
    return AnalyticsResult(
        task="drawdown",
        success=True,
        data={"drawdowns": drawdowns}
    )


async def _execute_allocation(user_assets: List[Asset]) -> AnalyticsResult:
    """Execute portfolio allocation calculation."""
    if not user_assets:
        return AnalyticsResult(task="allocation", success=False, error="No assets found.")
    
    current_prices = get_current_prices([a.symbol for a in user_assets])
    
    if not current_prices:
        return AnalyticsResult(task="allocation", success=False, error="Could not fetch current prices.")
    
    allocation = calculate_allocation(user_assets, current_prices)
    
    # Prepare pie chart data
    chart_data = {
        "type": "pie_chart",
        "labels": [a["symbol"] for a in allocation["allocations"]],
        "values": [a["percentage"] for a in allocation["allocations"]]
    }
    
    return AnalyticsResult(
        task="allocation",
        success=True,
        data={"allocation": allocation},
        chart_data=chart_data
    )
