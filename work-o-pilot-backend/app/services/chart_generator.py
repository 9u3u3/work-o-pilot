"""
Chart Generator Service
Generates static images (PNG base64) using Matplotlib for analytics results.
"""
import matplotlib.pyplot as plt
import io
import base64
import pandas as pd
from typing import Dict, Any, List, Optional
import matplotlib.dates as mdates

# Set non-interactive backend
plt.switch_backend('Agg')

# Style settings
plt.style.use('dark_background')
COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899']

def _fig_to_base64(fig) -> str:
    """Convert matplotlib figure to base64 string."""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=100, transparent=True)
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return img_str

def generate_trend_chart(data: Dict[str, Any], title: str = "Price Trend") -> Optional[str]:
    """
    Generate line chart for trends.
    Expected data structure: {"symbol": {"data_points": [{"date": "...", "close": 123}, ...]}}
    """
    try:
        fig, ax = plt.subplots(figsize=(10, 6))
        
        has_data = False
        for i, (symbol, trend_data) in enumerate(data.items()):
            points = trend_data.get("data_points", [])
            if not points:
                continue
                
            has_data = True
            df = pd.DataFrame(points)
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            
            ax.plot(df['date'], df['close'], label=symbol, color=COLORS[i % len(COLORS)], linewidth=2)
            
            # Add fill below line for single trend
            if len(data) == 1:
                ax.fill_between(df['date'], df['close'], alpha=0.2, color=COLORS[i % len(COLORS)])

        if not has_data:
            plt.close(fig)
            return None

        ax.set_title(title, fontsize=14, pad=20)
        ax.set_xlabel("Date", fontsize=10)
        ax.set_ylabel("Price", fontsize=10)
        ax.grid(True, linestyle='--', alpha=0.3)
        ax.legend()
        
        # Format dates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        fig.autofmt_xdate()
        
        # Remove spines
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        return _fig_to_base64(fig)
    except Exception as e:
        print(f"Error generating trend chart: {e}")
        return None

def generate_allocation_chart(data: Dict[str, Any], title: str = "Portfolio Allocation") -> Optional[str]:
    """
    Generate pie chart for allocation.
    Expected data structure: {"allocations": [{"symbol": "AAPL", "percentage": 50}, ...]}
    """
    try:
        allocations = data.get("allocations", [])
        if not allocations:
            return None
            
        labels = [item["symbol"] for item in allocations]
        sizes = [item["percentage"] for item in allocations]
        
        # Group small slices into "Other"
        if len(labels) > 8:
            main_labels = labels[:7]
            main_sizes = sizes[:7]
            other_size = sum(sizes[7:])
            if other_size > 0:
                main_labels.append("Other")
                main_sizes.append(other_size)
            labels = main_labels
            sizes = main_sizes

        fig, ax = plt.subplots(figsize=(8, 8))
        wedges, texts, autotexts = ax.pie(
            sizes, 
            labels=labels, 
            autopct='%1.1f%%',
            startangle=90,
            colors=COLORS,
            pctdistance=0.85,
            explode=[0.05] * len(labels) # Slight explosion for all
        )
        
        # Draw circle for donut chart
        centre_circle = plt.Circle((0,0), 0.70, fc='#1a1a1a') # Match dark background roughly
        fig.gca().add_artist(centre_circle)
        
        plt.setp(autotexts, size=9, weight="bold", color="white")
        plt.setp(texts, size=10, color="white")
        
        ax.set_title(title, fontsize=14, pad=20)
        ax.axis('equal')
        
        return _fig_to_base64(fig)
    except Exception as e:
        print(f"Error generating allocation chart: {e}")
        return None

def generate_bar_chart(data: Dict[str, Any], title: str = "Performance Ranking") -> Optional[str]:
    """
    Generate bar chart for rankings/comparisons.
    Expected data structure: {"rankings": [{"symbol": "AAPL", "change_percent": 10}, ...]}
    or {"assets": [{"symbol": "AAPL", "change_percent": 10}, ...]} for comparison
    """
    try:
        items = data.get("rankings", []) or data.get("assets", [])
        if not items:
            return None
            
        # Sort by change percent
        items.sort(key=lambda x: x.get("change_percent", 0), reverse=True)
        
        symbols = [item["symbol"] for item in items]
        values = [item.get("change_percent", 0) for item in items]
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Color bars based on positive/negative
        bar_colors = ['#10b981' if v >= 0 else '#ef4444' for v in values]
        
        bars = ax.bar(symbols, values, color=bar_colors, alpha=0.8)
        
        # Add value labels on top of bars
        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width()/2., 
                height,
                f'{height:.1f}%',
                ha='center', 
                va='bottom' if height > 0 else 'top',
                color='white',
                fontsize=9
            )
            
        ax.set_title(title, fontsize=14, pad=20)
        ax.set_ylabel("Change %", fontsize=10)
        ax.grid(True, axis='y', linestyle='--', alpha=0.3)
        
        # Remove spines
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_position('zero') # Move x-axis to 0
        
        return _fig_to_base64(fig)
    except Exception as e:
        print(f"Error generating bar chart: {e}")
        return None

def generate_forecast_chart(data: Dict[str, Any], title: str = "Price Forecast") -> Optional[str]:
    """
    Generate line chart for forecast with confidence intervals.
    """
    try:
        points = data.get("data_points", [])
        if not points:
            return None
            
        symbol = data.get("symbol", "Stock")
        
        df = pd.DataFrame(points)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Plot main line
        ax.plot(df['date'], df['close'], label='Forecast', color=COLORS[0], linewidth=2)
        
        # Plot confidence interval
        ax.fill_between(
            df['date'], 
            df['lower'], 
            df['upper'], 
            color=COLORS[0], 
            alpha=0.2,
            label='Confidence Interval'
        )
        
        ax.set_title(f"{title} - {symbol}", fontsize=14, pad=20)
        ax.set_xlabel("Date", fontsize=10)
        ax.set_ylabel("Price", fontsize=10)
        ax.grid(True, linestyle='--', alpha=0.3)
        ax.legend()
        
        # Format dates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        fig.autofmt_xdate()
        
        # Remove spines
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        return _fig_to_base64(fig)
    except Exception as e:
        print(f"Error generating forecast chart: {e}")
        return None


def generate_chart(visualization_type: str, data: Dict[str, Any]) -> Optional[str]:
    """
    Main entry point to generate chart based on type.
    """
    if visualization_type == "line_chart":
        # Check if it's a forecast
        if data.get("is_forecast"):
            return generate_forecast_chart(data)
            
        # Data might be nested under 'trends' or direct
        chart_data = data.get("trends", data)
        return generate_trend_chart(chart_data)
        
    elif visualization_type == "pie_chart":
        chart_data = data.get("allocation", data)
        return generate_allocation_chart(chart_data)
        
    elif visualization_type == "bar_chart":
        # Could be rankings or comparison
        if "rankings" in data:
            return generate_bar_chart(data.get("rankings", {}))
        elif "comparison" in data:
            return generate_bar_chart(data.get("comparison", {}))
        else:
            return generate_bar_chart(data)
            
    return None
