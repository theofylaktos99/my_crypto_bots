# zscore_phi_strategy.py - Z-Score Phi Strategy Implementation
import pandas as pd
import numpy as np
from typing import Dict, Any
import logging
from .base_strategy import BaseStrategy

logger = logging.getLogger(__name__)

class ZScorePhiStrategy(BaseStrategy):
    """
    Z-Score Phi (Golden Ratio) Mean Reversion Strategy
    
    Uses Z-score analysis combined with the golden ratio (1.618) for
    mean reversion trading signals.
    
    Entry Rules:
    - BUY: Z-Score < -entry_threshold (oversold)
    - SELL: Z-Score > +entry_threshold (overbought)
    - EXIT: Z-Score returns to within ±exit_threshold
    """
    
    def __init__(self, 
                 lookback: int = 21,
                 entry_threshold: float = 1.618,  # Golden ratio
                 exit_threshold: float = 0.618,   # Inverse golden ratio
                 volume_filter: bool = True):
        
        super().__init__("Z-Score Phi Strategy")
        
        # Strategy parameters
        self.lookback = lookback
        self.entry_threshold = entry_threshold
        self.exit_threshold = exit_threshold
        self.volume_filter = volume_filter
        
        # State tracking
        self.current_zscore = 0.0
        self.price_mean = 0.0
        self.price_std = 0.0
        self.volume_mean = 0.0
        
        # Performance tracking
        self.signals_generated = 0
        self.last_signal_price = 0.0
        
        logger.info(f"Initialized {self.name} with parameters:")
        logger.info(f"Lookback: {lookback}, Entry: {entry_threshold}, Exit: {exit_threshold}")
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate Z-score and related indicators"""
        try:
            df = data.copy()
            
            # Ensure we have required columns
            required_cols = ['close', 'volume']
            for col in required_cols:
                if col not in df.columns:
                    logger.error(f"Missing required column: {col}")
                    return df
            
            # Calculate rolling statistics
            df['price_mean'] = df['close'].rolling(window=self.lookback).mean()
            df['price_std'] = df['close'].rolling(window=self.lookback).std()
            
            # Calculate Z-score
            df['zscore'] = (df['close'] - df['price_mean']) / df['price_std']
            
            # Handle NaN values
            df['zscore'] = df['zscore'].fillna(0)
            
            # Calculate volume statistics if volume filter is enabled
            if self.volume_filter:
                df['volume_mean'] = df['volume'].rolling(window=self.lookback).mean()
                df['volume_ratio'] = df['volume'] / df['volume_mean']
                df['volume_ratio'] = df['volume_ratio'].fillna(1)
            
            # Calculate additional metrics
            df['price_momentum'] = df['close'].pct_change(5)  # 5-period momentum
            df['volatility'] = df['close'].rolling(window=self.lookback).std() / df['price_mean']
            
            # Store current values
            if len(df) > 0:
                latest = df.iloc[-1]
                self.current_zscore = latest.get('zscore', 0)
                self.price_mean = latest.get('price_mean', 0)
                self.price_std = latest.get('price_std', 0)
                if self.volume_filter:
                    self.volume_mean = latest.get('volume_mean', 0)
            
            return df
            
        except Exception as e:
            logger.error(f"Error calculating indicators: {e}")
            return data
    
    def generate_signal(self, data: pd.DataFrame) -> str:
        """Generate trading signal based on Z-score analysis"""
        try:
            # Calculate indicators
            df = self.calculate_indicators(data)
            
            if len(df) < self.lookback:
                return 'hold'
            
            current = df.iloc[-1]
            
            # Get current values
            zscore = current.get('zscore', 0)
            price = current.get('close', 0)
            volume_ratio = current.get('volume_ratio', 1) if self.volume_filter else 1
            price_momentum = current.get('price_momentum', 0)
            volatility = current.get('volatility', 0)
            
            # Check for invalid values
            if pd.isna(zscore) or abs(zscore) == np.inf:
                return 'hold'
            
            # Volume filter check
            if self.volume_filter and volume_ratio < 0.8:  # Below average volume
                return 'hold'
            
            # Exit conditions for existing positions
            if self.position != 0:
                # Exit long position
                if self.position > 0:
                    if (zscore > -self.exit_threshold or 
                        zscore > self.entry_threshold or
                        price_momentum < -0.02):  # Strong negative momentum
                        return 'close_long'
                
                # Exit short position
                elif self.position < 0:
                    if (zscore < self.exit_threshold or 
                        zscore < -self.entry_threshold or
                        price_momentum > 0.02):  # Strong positive momentum
                        return 'close_short'
            
            # Entry conditions (only if no position)
            if self.position == 0:
                # Additional filters
                volatility_ok = volatility > 0.01  # Minimum volatility threshold
                
                # Long entry: Oversold condition
                if (zscore < -self.entry_threshold and 
                    price_momentum <= 0 and  # No strong upward momentum
                    volatility_ok and
                    volume_ratio > 1.0):  # Above average volume
                    
                    self.last_signal_price = price
                    self.signals_generated += 1
                    
                    logger.info(f"LONG Signal: Z-Score={zscore:.2f}, Price={price:.4f}, Vol={volume_ratio:.2f}")
                    return 'buy'
                
                # Short entry: Overbought condition  
                elif (zscore > self.entry_threshold and 
                      price_momentum >= 0 and  # No strong downward momentum
                      volatility_ok and
                      volume_ratio > 1.0):  # Above average volume
                    
                    self.last_signal_price = price
                    self.signals_generated += 1
                    
                    logger.info(f"SHORT Signal: Z-Score={zscore:.2f}, Price={price:.4f}, Vol={volume_ratio:.2f}")
                    return 'sell'
            
            return 'hold'
            
        except Exception as e:
            logger.error(f"Error generating signal: {e}")
            return 'hold'
    
    def get_strategy_parameters(self) -> Dict[str, Any]:
        """Get current strategy parameters"""
        return {
            'lookback': self.lookback,
            'entry_threshold': self.entry_threshold,
            'exit_threshold': self.exit_threshold,
            'volume_filter': self.volume_filter
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
        return {
            'zscore': round(self.current_zscore, 3),
            'price_mean': round(self.price_mean, 2),
            'price_std': round(self.price_std, 2),
            'volume_mean': round(self.volume_mean, 2),
            'entry_threshold': self.entry_threshold,
            'exit_threshold': self.exit_threshold,
            'signals_generated': self.signals_generated
        }
    
    def get_signal_strength(self) -> float:
        """Get current signal strength (0-1)"""
        try:
            if abs(self.current_zscore) < self.exit_threshold:
                return 0.0  # No signal
            
            # Calculate strength based on Z-score magnitude
            strength = min(abs(self.current_zscore) / self.entry_threshold, 1.0)
            
            return round(strength, 2)
            
        except Exception as e:
            logger.error(f"Error calculating signal strength: {e}")
            return 0.0
    
    def validate_data(self, data: pd.DataFrame) -> bool:
        """Validate input data"""
        try:
            required_cols = ['close', 'volume']
            
            if not all(col in data.columns for col in required_cols):
                logger.error("Missing required columns")
                return False
            
            if len(data) < self.lookback + 10:
                logger.error("Insufficient data for strategy")
                return False
            
            # Check for NaN values
            if data[required_cols].isnull().any().any():
                logger.error("Data contains NaN values")
                return False
            
            # Check for zero standard deviation
            if len(data) >= self.lookback:
                recent_data = data['close'].tail(self.lookback)
                if recent_data.std() == 0:
                    logger.error("Zero price volatility detected")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating data: {e}")
            return False
    
    def get_strategy_info(self) -> Dict[str, Any]:
        """Get comprehensive strategy information"""
        base_info = super().get_strategy_info()
        
        # Add Z-Score specific info
        base_info.update({
            'current_zscore': round(self.current_zscore, 3),
            'signal_strength': self.get_signal_strength(),
            'signals_generated': self.signals_generated,
            'last_signal_price': self.last_signal_price,
            'strategy_type': 'Mean Reversion',
            'lookback_period': self.lookback,
            'entry_threshold': self.entry_threshold,
            'exit_threshold': self.exit_threshold
        })
        
        return base_info
    
    def reset_strategy(self):
        """Reset strategy state"""
        try:
            super().__init__(self.name)  # Reset base class
            
            # Reset Z-Score specific state
            self.current_zscore = 0.0
            self.price_mean = 0.0
            self.price_std = 0.0
            self.volume_mean = 0.0
            self.signals_generated = 0
            self.last_signal_price = 0.0
            
            logger.info(f"{self.name} strategy reset")
            
        except Exception as e:
            logger.error(f"Error resetting strategy: {e}")
