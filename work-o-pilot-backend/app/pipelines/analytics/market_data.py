"""
Market Data Service - yfinance wrapper
Fetches live stock data, keeps in memory only (no persistence)
"""
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from app.models.schemas import TimeRange


def get_period_string(time_range: TimeRange) -> str:
    """
    Convert TimeRange to yfinance period string.
    
    yfinance periods: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
    """
    unit = time_range.unit
    value = time_range.value or 1
    
    if unit == "days":
        if value <= 5:
            return f"{value}d"
        elif value <= 30:
            return "1mo"
        elif value <= 90:
            return "3mo"
        else:
            return "6mo"
    elif unit == "weeks":
        days = value * 7
        if days <= 30:
            return "1mo"
        elif days <= 90:
            return "3mo"
        else:
            return "6mo"
    elif unit == "months":
        if value <= 1:
            return "1mo"
        elif value <= 3:
            return "3mo"
        elif value <= 6:
            return "6mo"
        elif value <= 12:
            return "1y"
        elif value <= 24:
            return "2y"
        else:
            return "5y"
    elif unit == "years":
        if value <= 1:
            return "1y"
        elif value <= 2:
            return "2y"
        elif value <= 5:
            return "5y"
        else:
            return "10y"
    
    return "1mo"  # default


def get_interval_string(time_range: TimeRange) -> str:
    """
    Get appropriate interval based on time range.
    
    yfinance intervals: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
    """
    unit = time_range.unit
    value = time_range.value or 1
    
    total_days = 0
    if unit == "days":
        total_days = value
    elif unit == "weeks":
        total_days = value * 7
    elif unit == "months":
        total_days = value * 30
    elif unit == "years":
        total_days = value * 365
    
    if total_days <= 7:
        return "1h"
    elif total_days <= 60:
        return "1d"
    elif total_days <= 365:
        return "1d"
    else:
        return "1wk"


def fetch_stock_data(
    symbol: str,
    time_range: TimeRange,
    include_volume: bool = False
) -> Optional[pd.DataFrame]:
    """
    Fetch historical stock data for a single symbol.
    
    Args:
        symbol: Stock ticker symbol (e.g., "AAPL")
        time_range: TimeRange object specifying the period
        include_volume: Whether to include volume data
    
    Returns:
        DataFrame with columns: Date, Open, High, Low, Close, Volume (if requested)
        Returns None if fetch fails
    """
    try:
        ticker = yf.Ticker(symbol)
        period = get_period_string(time_range)
        interval = get_interval_string(time_range)
        
        df = ticker.history(period=period, interval=interval)
        
        if df.empty:
            return None
        
        # Reset index to get Date as column
        df = df.reset_index()
        
        # Rename columns for consistency
        if 'Datetime' in df.columns:
            df = df.rename(columns={'Datetime': 'Date'})
        
        # Select columns
        columns = ['Date', 'Open', 'High', 'Low', 'Close']
        if include_volume:
            columns.append('Volume')
        
        df = df[columns]
        df['Symbol'] = symbol
        
        return df
    
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None


def fetch_multiple_stocks(
    symbols: List[str],
    time_range: TimeRange
) -> Dict[str, pd.DataFrame]:
    """
    Fetch historical data for multiple symbols.
    
    Args:
        symbols: List of ticker symbols
        time_range: TimeRange object
    
    Returns:
        Dictionary mapping symbol to DataFrame
    """
    results = {}
    for symbol in symbols:
        df = fetch_stock_data(symbol, time_range)
        if df is not None:
            results[symbol] = df
    return results


def get_current_price(symbol: str) -> Optional[float]:
    """
    Get current/latest price for a symbol.
    
    Args:
        symbol: Stock ticker symbol
    
    Returns:
        Current price or None if unavailable
    """
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.fast_info
        return info.get('lastPrice') or info.get('regularMarketPrice')
    except Exception as e:
        print(f"Error getting current price for {symbol}: {e}")
        return None


def get_current_prices(symbols: List[str]) -> Dict[str, float]:
    """
    Get current prices for multiple symbols.
    
    Args:
        symbols: List of ticker symbols
    
    Returns:
        Dictionary mapping symbol to current price
    """
    prices = {}
    for symbol in symbols:
        price = get_current_price(symbol)
        if price is not None:
            prices[symbol] = price
    return prices


def validate_symbol(symbol: str) -> bool:
    """
    Check if a symbol is valid (exists in yfinance).
    
    Args:
        symbol: Stock ticker symbol
    
    Returns:
        True if valid, False otherwise
    """
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.fast_info
        return info is not None and hasattr(info, 'lastPrice')
    except:
        return False
