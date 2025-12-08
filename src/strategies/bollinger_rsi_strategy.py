# bollinger_rsi_strategy.py - Bollinger Bands + RSI Strategy
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
import logging
from .base_strategy import BaseStrategy, Signal
from utils.technical_indicators import RSI, BBANDS
from utils.logger import logger

class BollingerRSIStrategy(BaseStrategy):
    """
    Bollinger Bands + RSI Strategy
    
    Entry Rules:
    - Buy: Price touches lower Bollinger Band AND RSI < oversold_threshold
    - Sell: Price touches upper Bollinger Band AND RSI > overbought_threshold
    
    Exit Rules:
    - Exit long: RSI > exit_rsi_high OR price crosses middle band
    - Exit short: RSI < exit_rsi_low OR price crosses middle band
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        # Bollinger Bands parameters
        self.bb_period = config.get('bb_period', 20)
        self.bb_std = config.get('bb_std', 2.0)
        
        # RSI parameters
        self.rsi_period = config.get('rsi_period', 14)
        self.rsi_oversold = config.get('rsi_oversold', 30)
        self.rsi_overbought = config.get('rsi_overbought', 70)
        self.exit_rsi_low = config.get('exit_rsi_low', 40)
        self.exit_rsi_high = config.get('exit_rsi_high', 60)
        
        # Touch sensitivity (how close to bands counts as "touch")
        self.touch_sensitivity = config.get('touch_sensitivity', 0.02)  # 2%
        
        logger.info(f"BollingerRSIStrategy initialized: BB({self.bb_period}, {self.bb_std}), RSI({self.rsi_period})")
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate Bollinger Bands and RSI"""
        try:
            df = data.copy()
            
            # Calculate RSI
            df['rsi'] = RSI(df['close'], timeperiod=self.rsi_period)
            
            # Calculate Bollinger Bands
            bb_upper, bb_middle, bb_lower = BBANDS(
                df['close'], 
                timeperiod=self.bb_period,
                nbdevup=self.bb_std,
                nbdevdn=self.bb_std
            )
            
            df['bb_upper'] = bb_upper
            df['bb_middle'] = bb_middle
            df['bb_lower'] = bb_lower
            
            # Calculate band width (for volatility assessment)
            df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
            
            # Calculate price position within bands (0 = lower band, 1 = upper band)
            df['bb_position'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
            
            # Detect band touches
            df['touch_upper'] = (df['high'] >= df['bb_upper'] * (1 - self.touch_sensitivity))
            df['touch_lower'] = (df['low'] <= df['bb_lower'] * (1 + self.touch_sensitivity))
            
            # Store current indicators
            if len(df) > 0:
                latest = df.iloc[-1]
                self.indicators = {
                    'rsi': latest.get('rsi', 0),
                    'bb_upper': latest.get('bb_upper', 0),
                    'bb_middle': latest.get('bb_middle', 0),
                    'bb_lower': latest.get('bb_lower', 0),
                    'bb_width': latest.get('bb_width', 0),
                    'bb_position': latest.get('bb_position', 0),
                    'price': latest.get('close', 0)
                }
            
            return df
            
        except Exception as e:
            logger.error(f"Error calculating Bollinger RSI indicators: {e}")
            return data
    
    def generate_signal(self, data: pd.DataFrame) -> Optional[Signal]:
        """Generate trading signal based on Bollinger Bands and RSI"""
        try:
            df = self.calculate_indicators(data)
            
            min_data_points = max(self.bb_period, self.rsi_period) + 5
            if len(df) < min_data_points:
                return None
            
            latest = df.iloc[-1]
            current_price = latest['close']
            rsi = latest['rsi']
            bb_position = latest['bb_position']
            bb_width = latest['bb_width']
            
            # Check for valid values
            if pd.isna(rsi) or pd.isna(bb_position) or pd.isna(bb_width):
                return None
            
            # Assess market condition
            volatility = 'high' if bb_width > 0.1 else 'normal' if bb_width > 0.05 else 'low'
            
            # Buy signal: Price near lower band + RSI oversold
            if (latest['touch_lower'] or bb_position < 0.1) and rsi < self.rsi_oversold:
                confidence = self._calculate_confidence(rsi, bb_position, 'buy', volatility)
                
                return Signal(
                    action='buy',
                    confidence=confidence,
                    price=current_price,
                    timestamp=latest.name if hasattr(latest, 'name') else None,
                    metadata={
                        'rsi': rsi,
                        'bb_position': bb_position,
                        'bb_width': bb_width,
                        'volatility': volatility,
                        'signal_type': 'bollinger_rsi_buy',
                        'touch_lower': latest['touch_lower']
                    }
                )
            
            # Sell signal: Price near upper band + RSI overbought
            elif (latest['touch_upper'] or bb_position > 0.9) and rsi > self.rsi_overbought:
                confidence = self._calculate_confidence(rsi, bb_position, 'sell', volatility)
                
                return Signal(
                    action='sell',
                    confidence=confidence,
                    price=current_price,
                    timestamp=latest.name if hasattr(latest, 'name') else None,
                    metadata={
                        'rsi': rsi,
                        'bb_position': bb_position,
                        'bb_width': bb_width,
                        'volatility': volatility,
                        'signal_type': 'bollinger_rsi_sell',
                        'touch_upper': latest['touch_upper']
                    }
                )
            
            # Exit long signal: RSI high or price crosses middle band upward
            elif rsi > self.exit_rsi_high or (bb_position > 0.5 and latest['close'] > latest['bb_middle']):
                return Signal(
                    action='exit_long',
                    confidence=0.6,
                    price=current_price,
                    timestamp=latest.name if hasattr(latest, 'name') else None,
                    metadata={
                        'rsi': rsi,
                        'bb_position': bb_position,
                        'signal_type': 'exit_long',
                        'reason': 'rsi_high' if rsi > self.exit_rsi_high else 'middle_band_cross'
                    }
                )
            
            # Exit short signal: RSI low or price crosses middle band downward
            elif rsi < self.exit_rsi_low or (bb_position < 0.5 and latest['close'] < latest['bb_middle']):
                return Signal(
                    action='exit_short',
                    confidence=0.6,
                    price=current_price,
                    timestamp=latest.name if hasattr(latest, 'name') else None,
                    metadata={
                        'rsi': rsi,
                        'bb_position': bb_position,
                        'signal_type': 'exit_short',
                        'reason': 'rsi_low' if rsi < self.exit_rsi_low else 'middle_band_cross'
                    }
                )
            
            return Signal(
                action='hold',
                confidence=0.0,
                price=current_price,
                timestamp=latest.name if hasattr(latest, 'name') else None,
                metadata={
                    'rsi': rsi,
                    'bb_position': bb_position,
                    'bb_width': bb_width,
                    'volatility': volatility
                }
            )
            
        except Exception as e:
            logger.error(f"Error generating Bollinger RSI signal: {e}")
            return None
    
    def _calculate_confidence(self, rsi: float, bb_position: float, signal_type: str, volatility: str) -> float:
        """Calculate signal confidence based on indicator alignment"""
        confidence = 0.5  # Base confidence
        
        if signal_type == 'buy':
            # Higher confidence for more extreme RSI oversold
            rsi_factor = max(0, (self.rsi_oversold - rsi) / self.rsi_oversold)
            confidence += rsi_factor * 0.3
            
            # Higher confidence for closer to lower band
            bb_factor = max(0, (0.2 - bb_position) / 0.2)
            confidence += bb_factor * 0.2
            
        elif signal_type == 'sell':
            # Higher confidence for more extreme RSI overbought
            rsi_factor = max(0, (rsi - self.rsi_overbought) / (100 - self.rsi_overbought))
            confidence += rsi_factor * 0.3
            
            # Higher confidence for closer to upper band
            bb_factor = max(0, (bb_position - 0.8) / 0.2)
            confidence += bb_factor * 0.2
        
        # Adjust for volatility
        if volatility == 'high':
            confidence *= 1.1  # Slightly boost in high volatility
        elif volatility == 'low':
            confidence *= 0.9  # Slightly reduce in low volatility
        
        return min(confidence, 1.0)
    
    def get_current_indicators(self) -> Dict[str, float]:
        """Get current indicator values"""
        return self.indicators.copy()
    
    def get_strategy_info(self) -> Dict[str, Any]:
        """Get strategy information"""
        return {
            'name': 'Bollinger Bands + RSI',
            'type': 'mean_reversion',
            'parameters': {
                'bb_period': self.bb_period,
                'bb_std': self.bb_std,
                'rsi_period': self.rsi_period,
                'rsi_oversold': self.rsi_oversold,
                'rsi_overbought': self.rsi_overbought
            },
            'description': f'BB({self.bb_period},{self.bb_std}) + RSI({self.rsi_period}) mean reversion strategy'
        }
