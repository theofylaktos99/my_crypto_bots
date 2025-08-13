# base_strategy.py - Base Strategy Class
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple, Any
import pandas as pd
import numpy as np
import logging
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class Signal:
    """Trading signal class"""
    action: str  # 'buy', 'sell', 'hold', 'exit_long', 'exit_short'
    confidence: float  # 0.0 to 1.0
    price: float
    timestamp: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.action not in ['buy', 'sell', 'hold', 'exit_long', 'exit_short']:
            raise ValueError(f"Invalid signal action: {self.action}")
        
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got: {self.confidence}")
        
        if self.metadata is None:
            self.metadata = {}

class BaseStrategy(ABC):
    """Base class for all trading strategies"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = config.get('name', self.__class__.__name__)
        self.position = 0  # 0 = no position, 1 = long, -1 = short
        self.entry_price = 0.0
        self.stop_loss = 0.0
        self.take_profit = 0.0
        self.trade_history = []
        self.performance_metrics = {}
        self.indicators = {}  # Store current indicator values
        
        # Risk management defaults
        self.max_position_size = config.get('max_position_size', 1.0)
        self.risk_per_trade = config.get('risk_per_trade', 0.02)  # 2% risk per trade
        self.max_daily_loss = config.get('max_daily_loss', 0.05)  # 5% max daily loss
        
        logger.info(f"Initialized strategy: {self.name}")
    
    @abstractmethod
    def generate_signal(self, data: pd.DataFrame) -> Optional[Signal]:
        """
        Generate trading signal based on market data
        
        Args:
            data: OHLCV DataFrame with market data
            
        Returns:
            Signal: Trading signal object or None
        """
        pass
    
    @abstractmethod
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate technical indicators for the strategy
        
        Args:
            data: OHLCV DataFrame
            
        Returns:
            pd.DataFrame: Data with calculated indicators
        """
        pass
    
    def set_risk_parameters(self, risk_per_trade: float = None, 
                          max_position_size: float = None,
                          max_daily_loss: float = None):
        """Set risk management parameters"""
        if risk_per_trade:
            self.risk_per_trade = risk_per_trade
        if max_position_size:
            self.max_position_size = max_position_size
        if max_daily_loss:
            self.max_daily_loss = max_daily_loss
            
        logger.info(f"Updated risk parameters for {self.name}")
    
    def calculate_position_size(self, account_balance: float, 
                              entry_price: float, 
                              stop_loss_price: float) -> float:
        """
        Calculate position size based on risk management
        
        Args:
            account_balance: Current account balance
            entry_price: Planned entry price
            stop_loss_price: Stop loss price
            
        Returns:
            float: Position size
        """
        try:
            # Risk amount = account balance * risk per trade
            risk_amount = account_balance * self.risk_per_trade
            
            # Price difference (risk per unit)
            price_diff = abs(entry_price - stop_loss_price)
            
            if price_diff == 0:
                return 0.0
            
            # Position size = risk amount / price difference
            position_size = risk_amount / price_diff
            
            # Apply maximum position size constraint
            max_size = account_balance * self.max_position_size / entry_price
            position_size = min(position_size, max_size)
            
            return round(position_size, 8)
            
        except Exception as e:
            logger.error(f"Error calculating position size: {e}")
            return 0.0
    
    def update_position(self, signal: str, price: float, timestamp: datetime = None):
        """Update current position based on signal"""
        timestamp = timestamp or datetime.now()
        
        try:
            if signal == 'buy' and self.position <= 0:
                self.close_position(price, timestamp, 'buy_signal')
                self.position = 1
                self.entry_price = price
                self._log_trade('BUY', price, timestamp)
                
            elif signal == 'sell' and self.position >= 0:
                self.close_position(price, timestamp, 'sell_signal')
                self.position = -1
                self.entry_price = price
                self._log_trade('SELL', price, timestamp)
                
            elif signal in ['close_long', 'hold'] and self.position > 0:
                self.close_position(price, timestamp, signal)
                
            elif signal in ['close_short', 'hold'] and self.position < 0:
                self.close_position(price, timestamp, signal)
                
        except Exception as e:
            logger.error(f"Error updating position: {e}")
    
    def close_position(self, price: float, timestamp: datetime, reason: str):
        """Close current position"""
        if self.position == 0:
            return
            
        try:
            # Calculate P&L
            if self.position > 0:  # Long position
                pnl = (price - self.entry_price) / self.entry_price * 100
                side = 'LONG'
            else:  # Short position  
                pnl = (self.entry_price - price) / self.entry_price * 100
                side = 'SHORT'
            
            # Log the trade
            self._log_trade(f'CLOSE_{side}', price, timestamp, pnl, reason)
            
            # Reset position
            self.position = 0
            self.entry_price = 0.0
            self.stop_loss = 0.0
            self.take_profit = 0.0
            
        except Exception as e:
            logger.error(f"Error closing position: {e}")
    
    def _log_trade(self, action: str, price: float, timestamp: datetime, 
                   pnl: float = None, reason: str = None):
        """Log trade to history"""
        trade = {
            'timestamp': timestamp,
            'action': action,
            'price': price,
            'pnl_percent': pnl,
            'reason': reason,
            'position_after': self.position
        }
        
        self.trade_history.append(trade)
        
        log_msg = f"{action} @ {price:.4f}"
        if pnl is not None:
            log_msg += f" | P&L: {pnl:.2f}%"
        if reason:
            log_msg += f" | Reason: {reason}"
            
        logger.info(f"[{self.name}] {log_msg}")
    
    def calculate_performance(self) -> Dict[str, Any]:
        """Calculate strategy performance metrics"""
        try:
            if not self.trade_history:
                return {}
            
            # Filter only closed positions (trades with P&L)
            closed_trades = [t for t in self.trade_history if t.get('pnl_percent') is not None]
            
            if not closed_trades:
                return {}
            
            pnls = [t['pnl_percent'] for t in closed_trades]
            
            total_trades = len(closed_trades)
            winning_trades = len([p for p in pnls if p > 0])
            losing_trades = len([p for p in pnls if p < 0])
            
            total_return = sum(pnls)
            avg_return = np.mean(pnls)
            
            win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
            
            # Calculate Sharpe ratio (simplified)
            if len(pnls) > 1:
                sharpe_ratio = np.mean(pnls) / np.std(pnls) if np.std(pnls) != 0 else 0
            else:
                sharpe_ratio = 0
            
            # Max drawdown
            cumulative_returns = np.cumsum(pnls)
            running_max = np.maximum.accumulate(cumulative_returns)
            drawdowns = running_max - cumulative_returns
            max_drawdown = np.max(drawdowns) if len(drawdowns) > 0 else 0
            
            self.performance_metrics = {
                'total_trades': total_trades,
                'winning_trades': winning_trades,
                'losing_trades': losing_trades,
                'win_rate': round(win_rate, 2),
                'total_return': round(total_return, 2),
                'average_return': round(avg_return, 2),
                'sharpe_ratio': round(sharpe_ratio, 2),
                'max_drawdown': round(max_drawdown, 2),
                'profit_factor': self._calculate_profit_factor(pnls)
            }
            
            return self.performance_metrics
            
        except Exception as e:
            logger.error(f"Error calculating performance: {e}")
            return {}
    
    def _calculate_profit_factor(self, pnls: List[float]) -> float:
        """Calculate profit factor (gross profit / gross loss)"""
        try:
            gross_profit = sum([p for p in pnls if p > 0])
            gross_loss = abs(sum([p for p in pnls if p < 0]))
            
            if gross_loss == 0:
                return float('inf') if gross_profit > 0 else 0
            
            return round(gross_profit / gross_loss, 2)
            
        except Exception as e:
            logger.error(f"Error calculating profit factor: {e}")
            return 0.0
    
    def get_strategy_info(self) -> Dict[str, Any]:
        """Get strategy information"""
        return {
            'name': self.name,
            'current_position': self.position,
            'entry_price': self.entry_price,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
            'total_trades': len([t for t in self.trade_history if t.get('pnl_percent') is not None]),
            'risk_per_trade': self.risk_per_trade,
            'max_position_size': self.max_position_size
        }
    
    def get_current_indicators(self) -> Dict[str, float]:
        """Get current indicator values"""
        return self.indicators.copy()
    
    def reset_strategy(self):
        """Reset strategy state"""
        self.position = 0
        self.entry_price = 0.0
        self.stop_loss = 0.0
        self.take_profit = 0.0
        self.trade_history = []
        self.performance_metrics = {}
        self.indicators = {}
        logger.info(f"Strategy {self.name} reset")
