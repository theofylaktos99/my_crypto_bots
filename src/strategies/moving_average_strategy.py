# moving_average_strategy.py - Simple Moving Average Strategy
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
import logging
from .base_strategy import BaseStrategy, Signal
from utils.technical_indicators import SMA, EMA
from utils.logger import logger

class MovingAverageStrategy(BaseStrategy):
    """
    Simple Moving Average Crossover Strategy
    
    Buy when fast MA crosses above slow MA
    Sell when fast MA crosses below slow MA
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.fast_period = config.get('fast_period', 10)
        self.slow_period = config.get('slow_period', 30)
        self.ma_type = config.get('ma_type', 'sma').lower()  # 'sma' or 'ema'
        
        # Validation
        if self.fast_period >= self.slow_period:
            raise ValueError("Fast period must be less than slow period")
        
        logger.info(f"MovingAverageStrategy initialized: {self.fast_period}/{self.slow_period} {self.ma_type.upper()}")
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate moving averages"""
        try:
            df = data.copy()
            
            # Calculate moving averages
            if self.ma_type == 'ema':
                df['ma_fast'] = EMA(df['close'], timeperiod=self.fast_period)
                df['ma_slow'] = EMA(df['close'], timeperiod=self.slow_period)
            else:  # SMA
                df['ma_fast'] = SMA(df['close'], timeperiod=self.fast_period)
                df['ma_slow'] = SMA(df['close'], timeperiod=self.slow_period)
            
            # Calculate crossover signals
            df['ma_diff'] = df['ma_fast'] - df['ma_slow']
            df['ma_diff_prev'] = df['ma_diff'].shift(1)
            
            # Store current indicators
            if len(df) > 0:
                latest = df.iloc[-1]
                self.indicators = {
                    'ma_fast': latest.get('ma_fast', 0),
                    'ma_slow': latest.get('ma_slow', 0),
                    'ma_diff': latest.get('ma_diff', 0),
                    'price': latest.get('close', 0)
                }
            
            return df
            
        except Exception as e:
            logger.error(f"Error calculating MA indicators: {e}")
            return data
    
    def generate_signal(self, data: pd.DataFrame) -> Optional[Signal]:
        """Generate trading signal based on MA crossover"""
        try:
            df = self.calculate_indicators(data)
            
            if len(df) < max(self.fast_period, self.slow_period) + 2:
                return None
            
            latest = df.iloc[-1]
            previous = df.iloc[-2]
            
            ma_fast = latest['ma_fast']
            ma_slow = latest['ma_slow']
            ma_diff = latest['ma_diff']
            ma_diff_prev = previous['ma_diff']
            
            # Check for valid values
            if pd.isna(ma_fast) or pd.isna(ma_slow) or pd.isna(ma_diff) or pd.isna(ma_diff_prev):
                return None
            
            signal_strength = abs(ma_diff) / ma_slow  # Relative difference
            signal_strength = min(signal_strength, 1.0)  # Cap at 1.0
            
            # Golden Cross: Fast MA crosses above Slow MA
            if ma_diff_prev <= 0 and ma_diff > 0:
                return Signal(
                    action='buy',
                    confidence=signal_strength,
                    price=latest['close'],
                    timestamp=latest.name if hasattr(latest, 'name') else None,
                    metadata={
                        'ma_fast': ma_fast,
                        'ma_slow': ma_slow,
                        'crossover_type': 'golden_cross',
                        'signal_strength': signal_strength
                    }
                )
            
            # Death Cross: Fast MA crosses below Slow MA
            elif ma_diff_prev >= 0 and ma_diff < 0:
                return Signal(
                    action='sell',
                    confidence=signal_strength,
                    price=latest['close'],
                    timestamp=latest.name if hasattr(latest, 'name') else None,
                    metadata={
                        'ma_fast': ma_fast,
                        'ma_slow': ma_slow,
                        'crossover_type': 'death_cross',
                        'signal_strength': signal_strength
                    }
                )
            
            return Signal(
                action='hold',
                confidence=0.0,
                price=latest['close'],
                timestamp=latest.name if hasattr(latest, 'name') else None,
                metadata={
                    'ma_fast': ma_fast,
                    'ma_slow': ma_slow,
                    'ma_diff': ma_diff
                }
            )
            
        except Exception as e:
            logger.error(f"Error generating MA signal: {e}")
            return None
    
    def get_current_indicators(self) -> Dict[str, float]:
        """Get current indicator values"""
        return self.indicators.copy()
    
    def get_strategy_info(self) -> Dict[str, Any]:
        """Get strategy information"""
        return {
            'name': 'Moving Average Crossover',
            'type': 'trend_following',
            'parameters': {
                'fast_period': self.fast_period,
                'slow_period': self.slow_period,
                'ma_type': self.ma_type.upper()
            },
            'description': f'{self.fast_period}/{self.slow_period} {self.ma_type.upper()} crossover strategy'
        }
