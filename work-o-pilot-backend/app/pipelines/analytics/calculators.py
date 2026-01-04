"""
Calculators - All deterministic analytics calculations
NO AI involvement - pure Python/Pandas logic
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Literal
from app.models.schemas import Asset, TrendResult, PnLResult, RankResult


def calculate_trend(df: pd.DataFrame, symbol: str) -> TrendResult:
    """
    Calculate price trend for a stock.
    
    Args:
        df: DataFrame with Date and Close columns
        symbol: Stock symbol
    
    Returns:
        TrendResult with trend analysis
    """
    if df.empty or len(df) < 2:
        return TrendResult(
            symbol=symbol,
            start_price=0.0,
            end_price=0.0,
            change_absolute=0.0,
            change_percent=0.0,
            trend_direction="flat",
            data_points=[]
        )
    
    start_price = float(df['Close'].iloc[0])
    end_price = float(df['Close'].iloc[-1])
    change_absolute = end_price - start_price
    change_percent = (change_absolute / start_price) * 100 if start_price != 0 else 0
    
    # Determine trend direction
    if change_percent > 1:
        trend_direction = "up"
    elif change_percent < -1:
        trend_direction = "down"
    else:
        trend_direction = "flat"
    
    # Prepare data points for charting
    data_points = []
    for _, row in df.iterrows():
        data_points.append({
            "date": row['Date'].isoformat() if hasattr(row['Date'], 'isoformat') else str(row['Date']),
            "close": float(row['Close'])
        })
    
    return TrendResult(
        symbol=symbol,
        start_price=round(start_price, 2),
        end_price=round(end_price, 2),
        change_absolute=round(change_absolute, 2),
        change_percent=round(change_percent, 2),
        trend_direction=trend_direction,
        data_points=data_points
    )


def calculate_percentage_change(df: pd.DataFrame) -> Dict:
    """
    Calculate percentage change between first and last data points.
    
    Args:
        df: DataFrame with Close column
    
    Returns:
        Dict with change metrics
    """
    if df.empty or len(df) < 2:
        return {"change_percent": 0.0, "start": 0.0, "end": 0.0}
    
    start = float(df['Close'].iloc[0])
    end = float(df['Close'].iloc[-1])
    change_percent = ((end - start) / start) * 100 if start != 0 else 0
    
    return {
        "change_percent": round(change_percent, 2),
        "start": round(start, 2),
        "end": round(end, 2)
    }


def calculate_absolute_change(df: pd.DataFrame) -> Dict:
    """
    Calculate absolute price change.
    
    Args:
        df: DataFrame with Close column
    
    Returns:
        Dict with absolute change metrics
    """
    if df.empty or len(df) < 2:
        return {"change_absolute": 0.0, "start": 0.0, "end": 0.0}
    
    start = float(df['Close'].iloc[0])
    end = float(df['Close'].iloc[-1])
    
    return {
        "change_absolute": round(end - start, 2),
        "start": round(start, 2),
        "end": round(end, 2)
    }


def rank_by_performance(
    dfs: Dict[str, pd.DataFrame],
    direction: Literal["top", "bottom"] = "top",
    n: int = 5,
    metric: str = "change_percent"
) -> RankResult:
    """
    Rank stocks by performance.
    
    Args:
        dfs: Dict mapping symbol to DataFrame
        direction: "top" for best performers, "bottom" for worst
        n: Number of results to return
        metric: Metric to rank by (change_percent, change_absolute)
    
    Returns:
        RankResult with rankings
    """
    performances = []
    
    for symbol, df in dfs.items():
        if df.empty or len(df) < 2:
            continue
        
        change = calculate_percentage_change(df)
        performances.append({
            "symbol": symbol,
            "change_percent": change["change_percent"],
            "start_price": change["start"],
            "end_price": change["end"]
        })
    
    # Sort by performance
    reverse = (direction == "top")
    performances.sort(key=lambda x: x["change_percent"], reverse=reverse)
    
    # Take top N
    rankings = performances[:n]
    
    # Add rank numbers
    for i, item in enumerate(rankings):
        item["rank"] = i + 1
    
    return RankResult(
        rankings=rankings,
        direction=direction,
        metric=metric
    )


def calculate_unrealized_pnl(
    holdings: List[Asset],
    current_prices: Dict[str, float]
) -> Dict[str, PnLResult]:
    """
    Calculate unrealized P&L for holdings.
    
    Args:
        holdings: List of Asset objects
        current_prices: Dict mapping symbol to current price
    
    Returns:
        Dict mapping symbol to PnLResult
    """
    results = {}
    
    for asset in holdings:
        symbol = asset.symbol
        if symbol not in current_prices:
            continue
        
        current_price = current_prices[symbol]
        cost_basis = asset.quantity * asset.avg_buy_price
        current_value = asset.quantity * current_price
        unrealized_pnl = current_value - cost_basis
        pnl_percent = (unrealized_pnl / cost_basis) * 100 if cost_basis != 0 else 0
        
        results[symbol] = PnLResult(
            symbol=symbol,
            quantity=asset.quantity,
            avg_buy_price=round(asset.avg_buy_price, 2),
            current_price=round(current_price, 2),
            cost_basis=round(cost_basis, 2),
            current_value=round(current_value, 2),
            unrealized_pnl=round(unrealized_pnl, 2),
            pnl_percent=round(pnl_percent, 2)
        )
    
    return results


def calculate_total_pnl(pnl_results: Dict[str, PnLResult]) -> Dict:
    """
    Calculate total portfolio P&L from individual results.
    
    Args:
        pnl_results: Dict of PnLResult objects
    
    Returns:
        Dict with total P&L metrics
    """
    total_cost_basis = sum(r.cost_basis for r in pnl_results.values())
    total_current_value = sum(r.current_value for r in pnl_results.values())
    total_pnl = total_current_value - total_cost_basis
    total_pnl_percent = (total_pnl / total_cost_basis) * 100 if total_cost_basis != 0 else 0
    
    return {
        "total_cost_basis": round(total_cost_basis, 2),
        "total_current_value": round(total_current_value, 2),
        "total_unrealized_pnl": round(total_pnl, 2),
        "total_pnl_percent": round(total_pnl_percent, 2),
        "positions": len(pnl_results)
    }


def calculate_volatility(df: pd.DataFrame) -> float:
    """
    Calculate annualized volatility (standard deviation of daily returns).
    
    Args:
        df: DataFrame with Close column
    
    Returns:
        Annualized volatility as percentage
    """
    if df.empty or len(df) < 2:
        return 0.0
    
    # Calculate daily returns
    returns = df['Close'].pct_change().dropna()
    
    if len(returns) == 0:
        return 0.0
    
    # Annualize (252 trading days)
    daily_std = returns.std()
    annualized_volatility = daily_std * np.sqrt(252) * 100
    
    return round(annualized_volatility, 2)


def calculate_drawdown(df: pd.DataFrame) -> Dict:
    """
    Calculate maximum drawdown.
    
    Args:
        df: DataFrame with Close column
    
    Returns:
        Dict with drawdown metrics
    """
    if df.empty or len(df) < 2:
        return {"max_drawdown_percent": 0.0, "peak": 0.0, "trough": 0.0}
    
    # Calculate running maximum
    rolling_max = df['Close'].cummax()
    
    # Calculate drawdown
    drawdown = (df['Close'] - rolling_max) / rolling_max * 100
    
    # Find maximum drawdown
    max_drawdown = drawdown.min()
    max_dd_idx = drawdown.idxmin()
    
    # Find peak before max drawdown
    peak_idx = df.loc[:max_dd_idx, 'Close'].idxmax()
    peak = float(df.loc[peak_idx, 'Close'])
    trough = float(df.loc[max_dd_idx, 'Close'])
    
    return {
        "max_drawdown_percent": round(max_drawdown, 2),
        "peak": round(peak, 2),
        "trough": round(trough, 2)
    }


def calculate_allocation(holdings: List[Asset], current_prices: Dict[str, float]) -> Dict:
    """
    Calculate portfolio allocation percentages.
    
    Args:
        holdings: List of Asset objects
        current_prices: Dict mapping symbol to current price
    
    Returns:
        Dict with allocation data for pie chart
    """
    allocations = []
    total_value = 0.0
    
    for asset in holdings:
        if asset.symbol in current_prices:
            value = asset.quantity * current_prices[asset.symbol]
            total_value += value
            allocations.append({
                "symbol": asset.symbol,
                "value": value,
                "quantity": asset.quantity
            })
    
    # Calculate percentages
    for alloc in allocations:
        alloc["percentage"] = round((alloc["value"] / total_value) * 100, 2) if total_value > 0 else 0
        alloc["value"] = round(alloc["value"], 2)
    
    # Sort by percentage descending
    allocations.sort(key=lambda x: x["percentage"], reverse=True)
    
    return {
        "allocations": allocations,
        "total_value": round(total_value, 2)
    }


def compare_assets(dfs: Dict[str, pd.DataFrame]) -> Dict:
    """
    Compare multiple assets' performance.
    
    Args:
        dfs: Dict mapping symbol to DataFrame
    
    Returns:
        Dict with comparison data
    """
    comparison = []
    
    for symbol, df in dfs.items():
        if df.empty:
            continue
        
        trend = calculate_trend(df, symbol)
        volatility = calculate_volatility(df)
        drawdown = calculate_drawdown(df)
        
        comparison.append({
            "symbol": symbol,
            "start_price": trend.start_price,
            "end_price": trend.end_price,
            "change_percent": trend.change_percent,
            "trend_direction": trend.trend_direction,
            "volatility": volatility,
            "max_drawdown": drawdown["max_drawdown_percent"]
        })
    
    return {
        "assets": comparison,
        "count": len(comparison)
    }


def generate_chart_data(
    dfs: Dict[str, pd.DataFrame],
    chart_type: str = "line_chart"
) -> Dict:
    """
    Generate chart-ready data for visualization.
    
    Args:
        dfs: Dict mapping symbol to DataFrame
        chart_type: Type of chart
    
    Returns:
        Dict with chart data
    """
    if chart_type == "line_chart":
        series = []
        for symbol, df in dfs.items():
            if df.empty:
                continue
            
            data_points = []
            for _, row in df.iterrows():
                data_points.append({
                    "x": row['Date'].isoformat() if hasattr(row['Date'], 'isoformat') else str(row['Date']),
                    "y": round(float(row['Close']), 2)
                })
            
            series.append({
                "name": symbol,
                "data": data_points
            })
        
        return {"type": "line_chart", "series": series}
    
    elif chart_type == "bar_chart":
        labels = []
        values = []
        
        for symbol, df in dfs.items():
            if df.empty:
                continue
            
            change = calculate_percentage_change(df)
            labels.append(symbol)
            values.append(change["change_percent"])
        
        return {"type": "bar_chart", "labels": labels, "values": values}
    
    return {"type": chart_type, "data": {}}
