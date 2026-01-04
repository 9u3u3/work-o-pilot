"""
Forecasting Pipeline - Production Ready Module

This module provides a clean, reusable forecasting pipeline using Prophet.
It follows enterprise architecture principles:
- JSON-driven configuration
- No visualization (handled separately)
- Pure prediction engine
- Structured output for AI summarization
"""

import pandas as pd
import numpy as np
from prophet import Prophet
from datetime import datetime
from typing import Dict, Any, List, Optional
import json


class ForecastingPipeline:
    """
    Production-ready forecasting pipeline.
    
    - NO CSV/Excel reading (data passed in)
    - NO plotting (handled by visualization layer)
    - NO AI explanations (handled by Response Composer)
    - Pure prediction engine
    """

    def __init__(self):
        """Initialize pipeline."""
        self.model = None
        self.request = None
        self.historical_df = None

    def run_forecast(
        self, 
        forecast_request: Dict[str, Any],
        historical_dataframe: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        SINGLE ENTRY POINT - All forecasting goes through here.

        Args:
            forecast_request: JSON configuration for forecasting
            historical_dataframe: Cleaned historical data with 'ds' and 'y' columns

        Returns:
            Structured forecast result JSON
        """
        # Store inputs
        self.request = forecast_request
        self.historical_df = historical_dataframe.copy()

        # Step 1: Validate request
        self._validate_request()

        # Step 2: Validate data
        self._validate_data()

        # Step 3: Preprocess data
        preprocessed_df = self._preprocess_data()

        # Step 4: Initialize and train model
        self._train_model(preprocessed_df)

        # Step 5: Generate forecast
        forecast_df = self._generate_forecast(preprocessed_df)

        # Step 6: Compute metrics
        metrics = self._compute_metrics(forecast_df)

        # Step 7: Build output
        result = self._build_output(forecast_df, metrics)

        return result

    def _validate_request(self):
        """STEP 1 - Request Validation (Fail Fast)"""
        req = self.request

        # Check operation
        if req.get('operation') != 'forecast':
            raise ValueError(f"Invalid operation: {req.get('operation')}. Must be 'forecast'")

        # Check model type
        model_type = req.get('model', {}).get('type')
        if model_type != 'prophet':
            raise ValueError(f"Invalid model type: {model_type}. Only 'prophet' supported")

        # Check forecast horizon
        periods = req.get('forecast_horizon', {}).get('periods', 0)
        if periods <= 0:
            raise ValueError(f"Invalid forecast periods: {periods}. Must be > 0")

        # Check constraints
        max_horizon = req.get('constraints', {}).get('max_horizon_days', 365)
        if periods > max_horizon:
            raise ValueError(f"Forecast horizon {periods} exceeds max {max_horizon} days")

    def _validate_data(self):
        """STEP 2 - Data Sanity Checks"""
        df = self.historical_df
        req = self.request

        # Check required columns
        if 'ds' not in df.columns:
            raise ValueError("Missing required column: 'ds'")
        if 'y' not in df.columns:
            raise ValueError("Missing required column: 'y'")

        # Check data types
        if not pd.api.types.is_datetime64_any_dtype(df['ds']):
            raise ValueError("Column 'ds' must be datetime type")
        if not pd.api.types.is_numeric_dtype(df['y']):
            raise ValueError("Column 'y' must be numeric type")

        # Check minimum history
        min_points = req.get('constraints', {}).get('min_history_points', 60)
        if len(df) < min_points:
            raise ValueError(f"Insufficient history: {len(df)} points, need {min_points}")

        # Check regressors
        for regressor in req.get('regressors', []):
            reg_name = regressor.get('name')
            if reg_name not in df.columns:
                raise ValueError(f"Missing regressor column: '{reg_name}'")
            if not pd.api.types.is_numeric_dtype(df[reg_name]):
                raise ValueError(f"Regressor '{reg_name}' must be numeric")

    def _preprocess_data(self) -> pd.DataFrame:
        """STEP 3 - Preprocessing (NO model logic)"""
        df = self.historical_df.copy()

        # Sort by date
        df = df.sort_values('ds').reset_index(drop=True)

        # Drop null targets
        df = df.dropna(subset=['y'])

        # Normalize regressors if specified
        for regressor in self.request.get('regressors', []):
            reg_name = regressor.get('name')
            if regressor.get('normalize', False):
                mean = df[reg_name].mean()
                std = df[reg_name].std()
                if std != 0:
                    df[reg_name] = (df[reg_name] - mean) / std
                # Store normalization params for future use
                regressor['_mean'] = float(mean)
                regressor['_std'] = float(std)

        return df

    def _train_model(self, df: pd.DataFrame):
        """STEP 4 - Initialize and Train Prophet"""
        model_config = self.request.get('model', {})
        seasonality = model_config.get('seasonality', {})

        # Initialize Prophet with JSON-driven config
        self.model = Prophet(
            interval_width=model_config.get('interval_width', 0.95),
            daily_seasonality=seasonality.get('daily', False),
            weekly_seasonality=seasonality.get('weekly', True),
            yearly_seasonality=seasonality.get('yearly', True),
            changepoint_prior_scale=model_config.get('changepoint_prior_scale', 0.5),
            n_changepoints=model_config.get('n_changepoints', 50),
            seasonality_mode=model_config.get('seasonality_mode', 'multiplicative'),
            seasonality_prior_scale=model_config.get('seasonality_prior_scale', 1.0)
        )

        # Add regressors dynamically
        for regressor in self.request.get('regressors', []):
            self.model.add_regressor(regressor.get('name'))

        # Train model (NO evaluation, NO plotting)
        self.model.fit(df)

    def _generate_forecast(self, historical_df: pd.DataFrame) -> pd.DataFrame:
        """STEP 5 - Generate Future Dataframe and Forecast"""
        horizon = self.request.get('forecast_horizon', {})
        periods = horizon.get('periods')
        unit = horizon.get('unit', 'days')

        # Map unit to frequency
        freq_map = {'days': 'D', 'weeks': 'W', 'months': 'M'}
        freq = freq_map.get(unit, 'D')

        # Generate future dataframe
        future = self.model.make_future_dataframe(periods=periods, freq=freq)

        # Attach regressor values
        for regressor in self.request.get('regressors', []):
            reg_name = regressor.get('name')

            # Merge historical regressor values
            future = future.merge(
                historical_df[['ds', reg_name]],
                on='ds',
                how='left'
            )

            # For future dates without regressor values, use forward fill or zero
            if future[reg_name].isna().any():
                future[reg_name] = future[reg_name].ffill().fillna(0)

        # Execute forecast
        forecast = self.model.predict(future)

        # Extract only required columns
        forecast = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]

        return forecast

    def _compute_metrics(self, forecast_df: pd.DataFrame) -> Dict[str, Any]:
        """STEP 6 - Post-Forecast Metrics (Mandatory)"""
        # Get only future predictions (after last historical date)
        last_historical_date = self.historical_df['ds'].max()
        future_forecast = forecast_df[forecast_df['ds'] > last_historical_date].copy()

        if len(future_forecast) == 0:
            raise ValueError("No future predictions generated")

        # 1. Trend Direction
        first_pred = future_forecast['yhat'].iloc[0]
        last_pred = future_forecast['yhat'].iloc[-1]
        slope = (last_pred - first_pred) / len(future_forecast)

        if slope > 0.1:
            trend = "upward"
        elif slope < -0.1:
            trend = "downward"
        else:
            trend = "flat"

        # 2. Average Growth Rate
        pct_changes = future_forecast['yhat'].pct_change().dropna()
        avg_growth_rate = float(pct_changes.mean()) if len(pct_changes) > 0 else 0.0

        # 3. Volatility
        volatility_value = float(future_forecast['yhat'].std())

        # Categorize volatility
        volatility_thresholds = self.request.get('thresholds', {})
        low_threshold = volatility_thresholds.get('volatility_low', 5)
        medium_threshold = volatility_thresholds.get('volatility_medium', 15)

        if volatility_value < low_threshold:
            volatility = "low"
        elif volatility_value < medium_threshold:
            volatility = "medium"
        else:
            volatility = "high"

        # 4. Uncertainty Width
        uncertainty_width = float((future_forecast['yhat_upper'] - future_forecast['yhat_lower']).mean())

        # 5. Confidence Score (inverse of relative uncertainty)
        mean_prediction = float(future_forecast['yhat'].mean())
        relative_uncertainty = uncertainty_width / mean_prediction if mean_prediction != 0 else 1
        confidence_score = float(1 / (1 + relative_uncertainty))  # Normalized 0-1

        metrics = {
            "trend": trend,
            "avg_growth_rate": round(avg_growth_rate, 6),
            "volatility": volatility,
            "volatility_value": round(volatility_value, 2),
            "uncertainty_width": round(uncertainty_width, 2),
            "confidence": round(confidence_score, 4)
        }

        return metrics

    def _build_output(self, forecast_df: pd.DataFrame, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """STEP 7 - Final Output Structure"""
        # Get only future predictions
        last_historical_date = self.historical_df['ds'].max()
        future_forecast = forecast_df[forecast_df['ds'] > last_historical_date].copy()

        # Convert to list of dicts
        forecast_list = []
        for _, row in future_forecast.iterrows():
            forecast_list.append({
                "ds": row['ds'].strftime('%Y-%m-%d'),
                "yhat": round(float(row['yhat']), 2),
                "yhat_lower": round(float(row['yhat_lower']), 2),
                "yhat_upper": round(float(row['yhat_upper']), 2)
            })

        # Build metadata
        metadata = {
            "entity": self.request.get('entity'),
            "metric": self.request.get('metric'),
            "horizon_days": self.request.get('forecast_horizon', {}).get('periods'),
            "model": self.request.get('model', {}).get('type'),
            "last_updated": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "historical_records": len(self.historical_df),
            "forecast_records": len(future_forecast)
        }

        result = {
            "forecast": forecast_list,
            "metrics": metrics,
            "metadata": metadata
        }

        return result


def build_forecast_request(
    entity: str,
    metric: str,
    horizon_periods: int = 30,
    horizon_unit: str = "days",
    granularity: str = "daily",
    seasonality: Optional[Dict[str, bool]] = None,
    regressors: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Helper function to build a forecast request JSON from intent parameters.
    """
    if seasonality is None:
        seasonality = {"daily": False, "weekly": True, "yearly": False}
    
    if regressors is None:
        regressors = []
    
    return {
        "operation": "forecast",
        "entity": entity,
        "metric": metric,
        "historical_window": {
            "granularity": granularity
        },
        "forecast_horizon": {
            "periods": horizon_periods,
            "unit": horizon_unit
        },
        "model": {
            "type": "prophet",
            "interval_width": 0.95,
            "seasonality": seasonality,
            "changepoint_prior_scale": 0.05,  # Lower for more stable forecasts
            "n_changepoints": 25,
            "seasonality_mode": "additive",  # Better for stock prices
            "seasonality_prior_scale": 10.0
        },
        "regressors": regressors,
        "constraints": {
            "min_history_points": 60,
            "max_horizon_days": 365
        }
    }
