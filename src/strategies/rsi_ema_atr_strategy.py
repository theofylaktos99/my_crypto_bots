# rsi_ema_atr_strategy.py - RSI + EMA + ATR Strategy Implementation
import pandas as pd
import numpy as np
from typing import Dict, Any
import logging
from .base_strategy import BaseStrategy
from utils.technical_indicators import RSI, EMA, ATR

logger = logging.getLogger(__name__)

class RSIEMAATRStrategy(BaseStrategy):
    """
    RSI + EMA + ATR Trading Strategy
    
    Entry Rules:
    - BUY: RSI < oversold AND price > EMA AND volume > avg_volume
    - SELL: RSI > overbought OR stop-loss/take-profit hit
    
    Risk Management:
    - Dynamic stop-loss based on ATR
    - Dynamic take-profit based on ATR
    """
    
    def __init__(self, 
                 rsi_period: int = 14,
                 ema_period: int = 200,
                 atr_period: int = 14,
                 oversold_threshold: int = 30,
                 overbought_threshold: int = 70,
                 atr_stop_multiplier: float = 1.5,
                 atr_profit_multiplier: float = 2.0):
        
        super().__init__("RSI-EMA-ATR Strategy")
        
        # Strategy parameters
        self.rsi_period = rsi_period
        self.ema_period = ema_period
        self.atr_period = atr_period
        self.oversold_threshold = oversold_threshold
        self.overbought_threshold = overbought_threshold
        self.atr_stop_multiplier = atr_stop_multiplier
        self.atr_profit_multiplier = atr_profit_multiplier
        
        # Indicator storage
        self.indicators = {}
        
        logger.info(f"Initialized {self.name} with parameters:")
        logger.info(f"RSI: {rsi_period}, EMA: {ema_period}, ATR: {atr_period}")
        logger.info(f"Oversold: {oversold_threshold}, Overbought: {overbought_threshold}")
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate RSI, EMA, and ATR indicators"""
        try:
            df = data.copy()
            
            # Ensure we have the required columns
            required_cols = ['open', 'high', 'low', 'close', 'volume']
            for col in required_cols:
                if col not in df.columns:
                    logger.error(f"Missing required column: {col}")
                    return df
            
            # Calculate RSI
            df['rsi'] = RSI(df['close'], timeperiod=self.rsi_period)
            
            # Calculate EMA
            df['ema'] = EMA(df['close'], timeperiod=self.ema_period)
            
            # Calculate ATR
            df['atr'] = ATR(
                df['high'], 
                df['low'], 
                df['close'], 
                timeperiod=self.atr_period
            )
            
            # Calculate volume moving average
            from utils.technical_indicators import SMA
            df['volume_ma'] = SMA(df['volume'], timeperiod=20)
            
            # Calculate additional trend indicators
            df['ema_fast'] = EMA(df['close'], timeperiod=12)
            df['ema_slow'] = EMA(df['close'], timeperiod=26)
            
            # Store current indicators
            if len(df) > 0:
                latest = df.iloc[-1]
                self.indicators = {
                    'rsi': latest.get('rsi', 0),
                    'ema': latest.get('ema', 0),
                    'atr': latest.get('atr', 0),
                    'price': latest.get('close', 0),
                    'volume': latest.get('volume', 0),
                    'volume_ma': latest.get('volume_ma', 0),
                    'ema_fast': latest.get('ema_fast', 0),
                    'ema_slow': latest.get('ema_slow', 0)
                }
            
            return df
            
        except Exception as e:
            logger.error(f"Error calculating indicators: {e}")
            return data
    
    def generate_signal(self, data: pd.DataFrame) -> str:
        """Generate trading signal"""
        try:
            # Calculate indicators
            df = self.calculate_indicators(data)
            
            if len(df) < max(self.rsi_period, self.ema_period, self.atr_period):
                return 'hold'
            
            current = df.iloc[-1]
            
            # Get current values
            rsi = current.get('rsi', 0)
            price = current.get('close', 0)
            ema = current.get('ema', 0)
            atr = current.get('atr', 0)
            volume = current.get('volume', 0)
            volume_ma = current.get('volume_ma', 0)
            ema_fast = current.get('ema_fast', 0)
            ema_slow = current.get('ema_slow', 0)
            
            # Check for invalid values
            if any(pd.isna([rsi, price, ema, atr]) or val == 0 for val in [rsi, price, ema, atr]):
                return 'hold'
            
            # Update stop-loss and take-profit for existing positions
            if self.position != 0:
                self._update_stop_take_profit(price, atr)
                
                # Check exit conditions
                if self.position > 0:  # Long position
                    if (rsi >= self.overbought_threshold or 
                        price <= self.stop_loss or 
                        price >= self.take_profit or
                        ema_fast <= ema_slow):  # Trend reversal
                        return 'close_long'
                        
                elif self.position < 0:  # Short position
                    if (rsi <= self.oversold_threshold or 
                        price >= self.stop_loss or 
                        price <= self.take_profit or
                        ema_fast >= ema_slow):  # Trend reversal
                        return 'close_short'
            
            # Entry conditions
            if self.position == 0:
                # Volume filter
                volume_ok = volume > volume_ma * 1.2 if volume_ma > 0 else True
                
                # BUY conditions
                if (rsi < self.oversold_threshold and 
                    price > ema and 
                    ema_fast > ema_slow and  # Uptrend confirmation
                    volume_ok):
                    
                    # Set stop-loss and take-profit
                    self.stop_loss = price - (atr * self.atr_stop_multiplier)
                    self.take_profit = price + (atr * self.atr_profit_multiplier)
                    
                    logger.info(f"BUY Signal: RSI={rsi:.1f}, Price={price:.4f}, EMA={ema:.4f}")
                    return 'buy'
                
                # SELL conditions
                elif (rsi > self.overbought_threshold and 
                      price < ema and 
                      ema_fast < ema_slow and  # Downtrend confirmation
                      volume_ok):
                    
                    # Set stop-loss and take-profit for short
                    self.stop_loss = price + (atr * self.atr_stop_multiplier)
                    self.take_profit = price - (atr * self.atr_profit_multiplier)
                    
                    logger.info(f"SELL Signal: RSI={rsi:.1f}, Price={price:.4f}, EMA={ema:.4f}")
                    return 'sell'
            
            return 'hold'
            
        except Exception as e:
            logger.error(f"Error generating signal: {e}")
            return 'hold'
    
    def _update_stop_take_profit(self, current_price: float, atr: float):
        """Update trailing stop-loss and take-profit"""
        try:
            if self.position > 0:  # Long position
                # Trailing stop-loss (only move up)
                new_stop = current_price - (atr * self.atr_stop_multiplier)
                if new_stop > self.stop_loss:
                    self.stop_loss = new_stop
                    
            elif self.position < 0:  # Short position
                # Trailing stop-loss (only move down)
                new_stop = current_price + (atr * self.atr_stop_multiplier)
                if new_stop < self.stop_loss:
                    self.stop_loss = new_stop
                    
        except Exception as e:
            logger.error(f"Error updating stop/profit levels: {e}")
    
    def get_strategy_parameters(self) -> Dict[str, Any]:
        """Get current strategy parameters"""
        return {
            'rsi_period': self.rsi_period,
            'ema_period': self.ema_period,
            'atr_period': self.atr_period,
            'oversold_threshold': self.oversold_threshold,
            'overbought_threshold': self.overbought_threshold,
            'atr_stop_multiplier': self.atr_stop_multiplier,
            'atr_profit_multiplier': self.atr_profit_multiplier
        }
    
    def update_parameters(self, **kwargs):
        """Update strategy parameters"""
        for param, value in kwargs.items():
            if hasattr(self, param):
                setattr(self, param, value)
                logger.info(f"Updated {param} to {value}")
            else:
                logger.warning(f"Unknown parameter: {param}")
    
    def get_current_indicators(self) -> Dict[str, float]:
        """Get current indicator values"""
        return self.indicators.copy()
    
    def validate_data(self, data: pd.DataFrame) -> bool:
        """Validate input data"""
        try:
            required_cols = ['open', 'high', 'low', 'close', 'volume']
            
            if not all(col in data.columns for col in required_cols):
                logger.error("Missing required columns")
                return False
            
            if len(data) < max(self.rsi_period, self.ema_period, self.atr_period) + 10:
                logger.error("Insufficient data for strategy")
                return False
            
            # Check for NaN values
            if data[required_cols].isnull().any().any():
                logger.error("Data contains NaN values")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating data: {e}")
            return False
