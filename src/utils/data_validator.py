# data_validator.py - Data Validation Utilities
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union
import logging
from .error_handler import ValidationError

logger = logging.getLogger(__name__)

class DataValidator:
    """Data validation utilities for trading systems"""
    
    @staticmethod
    def validate_ohlcv_data(df: pd.DataFrame, required_columns: Optional[List[str]] = None) -> bool:
        """
        Validate OHLCV DataFrame structure and data quality
        
        Args:
            df: DataFrame to validate
            required_columns: List of required columns (default: ['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        
        Returns:
            bool: True if valid, raises ValidationError if not
        """
        if required_columns is None:
            required_columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        
        if df is None or df.empty:
            raise ValidationError("DataFrame is None or empty")
        
        # Check required columns
        missing_columns = set(required_columns) - set(df.columns)
        if missing_columns:
            raise ValidationError(f"Missing required columns: {missing_columns}")
        
        # Check for null values
        null_counts = df[required_columns].isnull().sum()
        if null_counts.sum() > 0:
            logger.warning(f"Found null values: {null_counts[null_counts > 0].to_dict()}")
        
        # Check OHLC logic (High >= Low, Close between High and Low, etc.)
        if 'open' in df.columns and 'high' in df.columns and 'low' in df.columns and 'close' in df.columns:
            invalid_ohlc = df[
                (df['high'] < df['low']) | 
                (df['high'] < df['open']) | 
                (df['high'] < df['close']) |
                (df['low'] > df['open']) |
                (df['low'] > df['close'])
            ]
            
            if not invalid_ohlc.empty:
                logger.warning(f"Found {len(invalid_ohlc)} rows with invalid OHLC data")
        
        # Check for negative prices
        price_columns = ['open', 'high', 'low', 'close']
        price_columns = [col for col in price_columns if col in df.columns]
        negative_prices = df[df[price_columns] < 0]
        if not negative_prices.empty:
            raise ValidationError(f"Found {len(negative_prices)} rows with negative prices")
        
        # Check for negative volume
        if 'volume' in df.columns:
            negative_volume = df[df['volume'] < 0]
            if not negative_volume.empty:
                raise ValidationError(f"Found {len(negative_volume)} rows with negative volume")
        
        return True
    
    @staticmethod
    def validate_price_data(price: Union[float, int]) -> bool:
        """Validate individual price value"""
        if price is None or np.isnan(price) or np.isinf(price):
            raise ValidationError(f"Invalid price value: {price}")
        
        if price <= 0:
            raise ValidationError(f"Price must be positive: {price}")
        
        return True
    
    @staticmethod
    def validate_quantity_data(quantity: Union[float, int]) -> bool:
        """Validate quantity/volume value"""
        if quantity is None or np.isnan(quantity) or np.isinf(quantity):
            raise ValidationError(f"Invalid quantity value: {quantity}")
        
        if quantity < 0:
            raise ValidationError(f"Quantity cannot be negative: {quantity}")
        
        return True
    
    @staticmethod
    def validate_timestamp_data(timestamp) -> bool:
        """Validate timestamp data"""
        if timestamp is None:
            raise ValidationError("Timestamp cannot be None")
        
        if isinstance(timestamp, str):
            try:
                pd.to_datetime(timestamp)
            except Exception as e:
                raise ValidationError(f"Invalid timestamp format: {timestamp}, error: {e}")
        
        return True
    
    @staticmethod
    def validate_config_data(config: Dict[str, Any], required_keys: List[str]) -> bool:
        """
        Validate configuration dictionary
        
        Args:
            config: Configuration dictionary
            required_keys: List of required keys
        
        Returns:
            bool: True if valid
        """
        if not isinstance(config, dict):
            raise ValidationError("Config must be a dictionary")
        
        missing_keys = set(required_keys) - set(config.keys())
        if missing_keys:
            raise ValidationError(f"Missing required config keys: {missing_keys}")
        
        return True
    
    @staticmethod
    def validate_trading_parameters(params: Dict[str, Any]) -> bool:
        """Validate trading parameters"""
        required_params = ['symbol', 'quantity', 'side']
        
        DataValidator.validate_config_data(params, required_params)
        
        # Validate side
        if params.get('side') not in ['buy', 'sell', 'long', 'short']:
            raise ValidationError(f"Invalid trading side: {params.get('side')}")
        
        # Validate quantity
        if 'quantity' in params:
            DataValidator.validate_quantity_data(params['quantity'])
        
        # Validate price if present
        if 'price' in params and params['price'] is not None:
            DataValidator.validate_price_data(params['price'])
        
        return True
    
    @staticmethod
    def clean_numeric_data(data: Union[pd.Series, np.ndarray, list]) -> Union[pd.Series, np.ndarray]:
        """
        Clean numeric data by removing NaN, infinity values
        
        Args:
            data: Input data
        
        Returns:
            Cleaned data
        """
        if isinstance(data, list):
            data = np.array(data)
        
        if isinstance(data, pd.Series):
            # Replace inf with NaN, then forward fill, then backward fill
            data = data.replace([np.inf, -np.inf], np.nan)
            data = data.ffill().bfill()
        
        elif isinstance(data, np.ndarray):
            # Replace inf with NaN
            data[np.isinf(data)] = np.nan
            # Forward fill using pandas
            temp_series = pd.Series(data).ffill().bfill()
            data = temp_series.values
        
        return data
    
    @staticmethod
    def validate_indicator_values(indicators: Dict[str, float]) -> bool:
        """Validate technical indicator values"""
        for name, value in indicators.items():
            if value is None or np.isnan(value) or np.isinf(value):
                logger.warning(f"Invalid indicator value for {name}: {value}")
                continue
        
        return True
    
    @staticmethod
    def validate_dataframe_index(df: pd.DataFrame, should_be_datetime: bool = True) -> bool:
        """Validate DataFrame index"""
        if df.index.empty:
            raise ValidationError("DataFrame index is empty")
        
        if should_be_datetime and not isinstance(df.index, pd.DatetimeIndex):
            logger.warning("DataFrame index is not DatetimeIndex")
        
        # Check for duplicated index
        if df.index.duplicated().any():
            logger.warning("Found duplicated index values")
        
        return True
