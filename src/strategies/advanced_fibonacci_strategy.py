# advanced_fibonacci_strategy.py - Advanced Fibonacci Retracement Strategy
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List, Tuple
import logging
from .base_strategy import BaseStrategy, Signal
from datetime import datetime

logger = logging.getLogger(__name__)

class AdvancedFibonacciStrategy(BaseStrategy):
    """
    Advanced Fibonacci Retracement Strategy with Multi-Timeframe Analysis
    
    Uses Fibonacci ratios (0.236, 0.382, 0.500, 0.618, 0.786) to identify
    support/resistance levels and generate high-probability trading signals.
    
    Key Features:
    - Automatic swing high/low detection
    - Multi-timeframe confluence
    - Dynamic position sizing based on Fibonacci levels
    - Adaptive stop-loss and take-profit placement
    """
    
    # Fibonacci ratios
    FIB_RATIOS = [0.000, 0.236, 0.382, 0.500, 0.618, 0.786, 1.000]
    FIB_EXTENSIONS = [1.272, 1.414, 1.618, 2.000, 2.618]
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize Fibonacci strategy"""
        super().__init__(config)
        
        # Strategy parameters
        self.lookback_period = config.get('lookback_period', 50)
        self.min_swing_size = config.get('min_swing_size', 0.02)  # 2% minimum swing
        self.confluence_threshold = config.get('confluence_threshold', 0.015)  # 1.5% price range
        self.volume_confirmation = config.get('volume_confirmation', True)
        
        # State variables
        self.swing_high = None
        self.swing_low = None
        self.fib_levels = {}
        self.fib_extensions_levels = {}
        self.current_trend = None  # 'up', 'down', or None
        self.support_levels = []
        self.resistance_levels = []
        
        logger.info(f"Initialized {self.name} - Advanced Fibonacci Strategy")
        logger.info(f"Parameters: lookback={self.lookback_period}, min_swing={self.min_swing_size}")
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate Fibonacci levels and related indicators"""
        try:
            df = data.copy()
            
            # Detect swing highs and lows
            df = self._detect_swings(df)
            
            # Calculate trend
            df = self._calculate_trend(df)
            
            # Calculate volatility for dynamic thresholds
            df['volatility'] = df['close'].pct_change().rolling(window=20).std()
            
            # Calculate volume profile
            df['volume_ma'] = df['volume'].rolling(window=20).mean()
            df['volume_ratio'] = df['volume'] / df['volume_ma']
            
            # Calculate RSI for confluence
            df = self._calculate_rsi(df, period=14)
            
            # Calculate MACD for trend confirmation
            df = self._calculate_macd(df)
            
            # Update Fibonacci levels
            if len(df) >= self.lookback_period:
                self._update_fibonacci_levels(df)
            
            # Store current indicators
            if len(df) > 0:
                latest = df.iloc[-1]
                self.indicators = {
                    'price': latest['close'],
                    'trend': self.current_trend,
                    'swing_high': self.swing_high,
                    'swing_low': self.swing_low,
                    'rsi': latest.get('rsi', 50),
                    'macd': latest.get('macd', 0),
                    'macd_signal': latest.get('macd_signal', 0),
                    'volume_ratio': latest.get('volume_ratio', 1.0),
                    'volatility': latest.get('volatility', 0)
                }
            
            return df
            
        except Exception as e:
            logger.error(f"Error calculating indicators: {e}")
            return data
    
    def _detect_swings(self, df: pd.DataFrame, window: int = 5) -> pd.DataFrame:
        """Detect swing highs and lows using local maxima/minima"""
        try:
            # Swing high: price is highest in window
            df['swing_high'] = df['high'].rolling(window=window*2+1, center=True).max() == df['high']
            
            # Swing low: price is lowest in window
            df['swing_low'] = df['low'].rolling(window=window*2+1, center=True).min() == df['low']
            
            return df
            
        except Exception as e:
            logger.error(f"Error detecting swings: {e}")
            return df
    
    def _calculate_trend(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate current market trend"""
        try:
            # Use EMA crossover for trend
            df['ema_fast'] = df['close'].ewm(span=12, adjust=False).mean()
            df['ema_slow'] = df['close'].ewm(span=26, adjust=False).mean()
            
            # Determine trend
            if len(df) > 0:
                latest = df.iloc[-1]
                if latest['ema_fast'] > latest['ema_slow']:
                    self.current_trend = 'up'
                elif latest['ema_fast'] < latest['ema_slow']:
                    self.current_trend = 'down'
                else:
                    self.current_trend = None
            
            return df
            
        except Exception as e:
            logger.error(f"Error calculating trend: {e}")
            return df
    
    def _calculate_rsi(self, df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """Calculate RSI indicator"""
        try:
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            
            rs = gain / loss
            df['rsi'] = 100 - (100 / (1 + rs))
            df['rsi'] = df['rsi'].fillna(50)
            
            return df
            
        except Exception as e:
            logger.error(f"Error calculating RSI: {e}")
            return df
    
    def _calculate_macd(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate MACD indicator"""
        try:
            exp1 = df['close'].ewm(span=12, adjust=False).mean()
            exp2 = df['close'].ewm(span=26, adjust=False).mean()
            
            df['macd'] = exp1 - exp2
            df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
            df['macd_histogram'] = df['macd'] - df['macd_signal']
            
            return df
            
        except Exception as e:
            logger.error(f"Error calculating MACD: {e}")
            return df
    
    def _update_fibonacci_levels(self, df: pd.DataFrame):
        """Update Fibonacci retracement and extension levels"""
        try:
            # Get recent price range
            recent_data = df.tail(self.lookback_period)
            
            # Find significant swing high and low
            swing_highs = recent_data[recent_data['swing_high'] == True]
            swing_lows = recent_data[recent_data['swing_low'] == True]
            
            if len(swing_highs) > 0 and len(swing_lows) > 0:
                # Get most recent significant swings
                recent_high = swing_highs['high'].iloc[-1]
                recent_low = swing_lows['low'].iloc[-1]
                
                # Check if swing is significant enough
                swing_size = abs(recent_high - recent_low) / recent_low
                
                if swing_size >= self.min_swing_size:
                    self.swing_high = recent_high
                    self.swing_low = recent_low
                    
                    # Calculate Fibonacci retracement levels
                    price_range = self.swing_high - self.swing_low
                    
                    self.fib_levels = {}
                    self.support_levels = []
                    self.resistance_levels = []
                    
                    # Determine if trend is up or down based on which came last
                    high_idx = swing_highs.index[-1]
                    low_idx = swing_lows.index[-1]
                    
                    if high_idx > low_idx:
                        # Downtrend - calculate retracements from high
                        for ratio in self.FIB_RATIOS:
                            level = self.swing_high - (price_range * ratio)
                            self.fib_levels[f'{ratio:.3f}'] = level
                            if ratio < 0.5:
                                self.resistance_levels.append(level)
                            elif ratio > 0.5:
                                self.support_levels.append(level)
                        
                        # Calculate extensions below low
                        for ext_ratio in self.FIB_EXTENSIONS:
                            level = self.swing_high - (price_range * ext_ratio)
                            self.fib_extensions_levels[f'{ext_ratio:.3f}'] = level
                            self.support_levels.append(level)
                    else:
                        # Uptrend - calculate retracements from low
                        for ratio in self.FIB_RATIOS:
                            level = self.swing_low + (price_range * ratio)
                            self.fib_levels[f'{ratio:.3f}'] = level
                            if ratio < 0.5:
                                self.support_levels.append(level)
                            elif ratio > 0.5:
                                self.resistance_levels.append(level)
                        
                        # Calculate extensions above high
                        for ext_ratio in self.FIB_EXTENSIONS:
                            level = self.swing_low + (price_range * ext_ratio)
                            self.fib_extensions_levels[f'{ext_ratio:.3f}'] = level
                            self.resistance_levels.append(level)
            
        except Exception as e:
            logger.error(f"Error updating Fibonacci levels: {e}")
    
    def _check_level_confluence(self, price: float, levels: List[float]) -> Optional[float]:
        """Check if price is near any Fibonacci level (confluence)"""
        try:
            for level in levels:
                price_diff = abs(price - level) / price
                if price_diff <= self.confluence_threshold:
                    return level
            return None
            
        except Exception as e:
            logger.error(f"Error checking confluence: {e}")
            return None
    
    def generate_signal(self, data: pd.DataFrame) -> Optional[Signal]:
        """Generate trading signal based on Fibonacci analysis"""
        try:
            # Calculate all indicators
            df = self.calculate_indicators(data)
            
            if len(df) < self.lookback_period:
                return None
            
            current = df.iloc[-1]
            price = current['close']
            
            # Check if we have valid Fibonacci levels
            if not self.fib_levels or self.swing_high is None or self.swing_low is None:
                return None
            
            # Get current indicators
            rsi = current.get('rsi', 50)
            macd = current.get('macd', 0)
            macd_signal = current.get('macd_signal', 0)
            volume_ratio = current.get('volume_ratio', 1.0)
            
            # Volume confirmation
            volume_ok = not self.volume_confirmation or volume_ratio > 1.0
            
            # Check for signals at Fibonacci levels
            signal = None
            confidence = 0.0
            metadata = {}
            
            # LONG SIGNAL CONDITIONS
            # Price at support level + bullish indicators
            support_level = self._check_level_confluence(price, self.support_levels)
            
            if support_level and self.position == 0:
                # Check bullish confluence
                bullish_signals = 0
                
                # RSI oversold
                if rsi < 35:
                    bullish_signals += 1
                    
                # MACD bullish crossover
                if macd > macd_signal:
                    bullish_signals += 1
                
                # Volume confirmation
                if volume_ok:
                    bullish_signals += 1
                
                # Price above key Fibonacci level (0.618 or 0.786)
                fib_618 = self.fib_levels.get('0.618', 0)
                fib_786 = self.fib_levels.get('0.786', 0)
                if price >= min(fib_618, fib_786):
                    bullish_signals += 1
                
                # Calculate confidence
                confidence = min(bullish_signals / 4.0, 1.0)
                
                if confidence >= 0.6:  # At least 60% confidence
                    # Calculate stop-loss and take-profit
                    price_range = self.swing_high - self.swing_low
                    stop_loss = price - (price_range * 0.1)  # 10% of range
                    take_profit = price + (price_range * 0.236)  # First Fib target
                    
                    metadata = {
                        'fib_level': support_level,
                        'stop_loss': stop_loss,
                        'take_profit': take_profit,
                        'rsi': rsi,
                        'macd': macd,
                        'confluence_count': bullish_signals
                    }
                    
                    signal = Signal(
                        action='buy',
                        confidence=confidence,
                        price=price,
                        timestamp=datetime.now(),
                        metadata=metadata
                    )
                    
                    logger.info(f"LONG Signal @ {price:.2f} | Fib Level: {support_level:.2f} | Confidence: {confidence:.2%}")
            
            # SHORT SIGNAL CONDITIONS
            # Price at resistance level + bearish indicators
            resistance_level = self._check_level_confluence(price, self.resistance_levels)
            
            if resistance_level and self.position == 0:
                # Check bearish confluence
                bearish_signals = 0
                
                # RSI overbought
                if rsi > 65:
                    bearish_signals += 1
                
                # MACD bearish crossover
                if macd < macd_signal:
                    bearish_signals += 1
                
                # Volume confirmation
                if volume_ok:
                    bearish_signals += 1
                
                # Price below key Fibonacci level
                fib_382 = self.fib_levels.get('0.382', 0)
                if price <= fib_382:
                    bearish_signals += 1
                
                # Calculate confidence
                confidence = min(bearish_signals / 4.0, 1.0)
                
                if confidence >= 0.6:
                    # Calculate stop-loss and take-profit
                    price_range = self.swing_high - self.swing_low
                    stop_loss = price + (price_range * 0.1)
                    take_profit = price - (price_range * 0.236)
                    
                    metadata = {
                        'fib_level': resistance_level,
                        'stop_loss': stop_loss,
                        'take_profit': take_profit,
                        'rsi': rsi,
                        'macd': macd,
                        'confluence_count': bearish_signals
                    }
                    
                    signal = Signal(
                        action='sell',
                        confidence=confidence,
                        price=price,
                        timestamp=datetime.now(),
                        metadata=metadata
                    )
                    
                    logger.info(f"SHORT Signal @ {price:.2f} | Fib Level: {resistance_level:.2f} | Confidence: {confidence:.2%}")
            
            # EXIT SIGNALS for existing positions
            if self.position != 0:
                exit_signal = self._check_exit_conditions(current)
                if exit_signal:
                    return exit_signal
            
            return signal
            
        except Exception as e:
            logger.error(f"Error generating signal: {e}")
            return None
    
    def _check_exit_conditions(self, current: pd.Series) -> Optional[Signal]:
        """Check if exit conditions are met"""
        try:
            price = current['close']
            
            # Exit long position
            if self.position > 0:
                # Stop-loss or take-profit hit
                if self.stop_loss and price <= self.stop_loss:
                    return Signal(
                        action='exit_long',
                        confidence=1.0,
                        price=price,
                        timestamp=datetime.now(),
                        metadata={'reason': 'stop_loss'}
                    )
                
                if self.take_profit and price >= self.take_profit:
                    return Signal(
                        action='exit_long',
                        confidence=1.0,
                        price=price,
                        timestamp=datetime.now(),
                        metadata={'reason': 'take_profit'}
                    )
                
                # Price hit resistance
                resistance = self._check_level_confluence(price, self.resistance_levels)
                if resistance:
                    return Signal(
                        action='exit_long',
                        confidence=0.8,
                        price=price,
                        timestamp=datetime.now(),
                        metadata={'reason': 'resistance_level', 'level': resistance}
                    )
            
            # Exit short position
            elif self.position < 0:
                if self.stop_loss and price >= self.stop_loss:
                    return Signal(
                        action='exit_short',
                        confidence=1.0,
                        price=price,
                        timestamp=datetime.now(),
                        metadata={'reason': 'stop_loss'}
                    )
                
                if self.take_profit and price <= self.take_profit:
                    return Signal(
                        action='exit_short',
                        confidence=1.0,
                        price=price,
                        timestamp=datetime.now(),
                        metadata={'reason': 'take_profit'}
                    )
                
                # Price hit support
                support = self._check_level_confluence(price, self.support_levels)
                if support:
                    return Signal(
                        action='exit_short',
                        confidence=0.8,
                        price=price,
                        timestamp=datetime.now(),
                        metadata={'reason': 'support_level', 'level': support}
                    )
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking exit conditions: {e}")
            return None
    
    def get_fibonacci_levels(self) -> Dict[str, Any]:
        """Get current Fibonacci levels for visualization"""
        return {
            'retracements': self.fib_levels,
            'extensions': self.fib_extensions_levels,
            'swing_high': self.swing_high,
            'swing_low': self.swing_low,
            'support_levels': self.support_levels,
            'resistance_levels': self.resistance_levels
        }
    
    def get_strategy_info(self) -> Dict[str, Any]:
        """Get comprehensive strategy information"""
        base_info = super().get_strategy_info()
        
        base_info.update({
            'strategy_type': 'Fibonacci Retracement',
            'trend': self.current_trend,
            'swing_high': self.swing_high,
            'swing_low': self.swing_low,
            'fib_levels_count': len(self.fib_levels),
            'support_levels_count': len(self.support_levels),
            'resistance_levels_count': len(self.resistance_levels)
        })
        
        return base_info
