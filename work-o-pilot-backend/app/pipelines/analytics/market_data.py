"""
Market Data Service - yfinance wrapper
Fetches live stock data, keeps in memory only (no persistence)
Supports: Stocks, Crypto, Gold, Silver, Oil, and other commodities
"""
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Tuple
from app.models.schemas import TimeRange


# ========================
# Asset Type Mappings
# ========================

# Map user-friendly names to yfinance tickers
ASSET_SYMBOL_MAP = {
    # Crypto
    "BTC": "BTC-USD", "BITCOIN": "BTC-USD",
    "ETH": "ETH-USD", "ETHEREUM": "ETH-USD",
    "SOL": "SOL-USD", "SOLANA": "SOL-USD",
    "XRP": "XRP-USD", "RIPPLE": "XRP-USD",
    "ADA": "ADA-USD", "CARDANO": "ADA-USD",
    "DOGE": "DOGE-USD", "DOGECOIN": "DOGE-USD",
    "DOT": "DOT-USD", "POLKADOT": "DOT-USD",
    "MATIC": "MATIC-USD", "POLYGON": "MATIC-USD",
    "AVAX": "AVAX-USD", "AVALANCHE": "AVAX-USD",
    "LINK": "LINK-USD", "CHAINLINK": "LINK-USD",
    "LTC": "LTC-USD", "LITECOIN": "LTC-USD",
    "UNI": "UNI-USD", "UNISWAP": "UNI-USD",
    "SHIB": "SHIB-USD",
    "PEPE": "PEPE-USD",
    
    # Precious Metals
    "GOLD": "GC=F", "XAU": "GC=F", "XAUUSD": "GC=F",
    "SILVER": "SI=F", "XAG": "SI=F", "XAGUSD": "SI=F",
    "PLATINUM": "PL=F", "XPT": "PL=F",
    "PALLADIUM": "PA=F", "XPD": "PA=F",
    
    # Energy
    "OIL": "CL=F", "CRUDE": "CL=F", "CRUDEOIL": "CL=F", "WTI": "CL=F",
    "BRENT": "BZ=F",
    "NATURALGAS": "NG=F", "NATGAS": "NG=F", "GAS": "NG=F",
    
    # ETF alternatives (more reliable data)
    "GLD": "GLD",  # Gold ETF
    "SLV": "SLV",  # Silver ETF
    "USO": "USO",  # Oil ETF
}

# Identify asset type by ticker pattern
CRYPTO_SUFFIXES = ["-USD", "-USDT", "-EUR", "-GBP"]
FUTURES_SUFFIXES = ["=F"]
COMMODITY_TICKERS = {"GC=F", "SI=F", "CL=F", "NG=F", "PL=F", "PA=F", "BZ=F"}
COMMODITY_ETFS = {"GLD", "SLV", "USO", "UNG", "DBA", "DBC"}


def normalize_symbol(symbol: str) -> str:
    """
    Convert user-friendly asset names to yfinance tickers.
    
    Examples:
        - "Bitcoin" -> "BTC-USD"
        - "Gold" -> "GC=F"
        - "AAPL" -> "AAPL" (unchanged)
    """
    upper = symbol.upper().strip()
    
    # Check if it's in our mapping
    if upper in ASSET_SYMBOL_MAP:
        return ASSET_SYMBOL_MAP[upper]
    
    # Already a valid ticker format
    return upper


def get_asset_type(symbol: str) -> str:
    """
    Detect the asset type from a ticker symbol.
    
    Returns: "stock", "crypto", "gold", "silver", "oil", "commodity"
    """
    upper = symbol.upper()
    
    # Check if it's crypto (has -USD suffix)
    for suffix in CRYPTO_SUFFIXES:
        if upper.endswith(suffix):
            return "crypto"
    
    # Check specific commodities
    if upper in {"GC=F", "GLD"}:
        return "gold"
    if upper in {"SI=F", "SLV"}:
        return "silver"
    if upper in {"CL=F", "BZ=F", "USO"}:
        return "oil"
    if upper in COMMODITY_TICKERS or upper in COMMODITY_ETFS:
        return "commodity"
    
    # Default to stock
    return "stock"


def get_data_source_name(symbol: str) -> str:
    """Get a human-readable data source name for a symbol."""
    asset_type = get_asset_type(symbol)
    
    if asset_type == "crypto":
        return f"CoinGecko/Yahoo Finance - {symbol}"
    elif asset_type in ("gold", "silver", "oil", "commodity"):
        return f"COMEX/Yahoo Finance - {symbol}"
    else:
        return f"Yahoo Finance - {symbol}"



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
