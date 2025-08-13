# backtesting_bot.py - Backtesting Bot Implementation
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List, Tuple
import logging
from datetime import datetime, timedelta
from .base_bot import BaseBot
from ..strategies.base_strategy import BaseStrategy
from ..utils.logger import logger
from ..utils.performance_analyzer import PerformanceAnalyzer
from ..utils.data_validator import DataValidator

class BacktestingBot(BaseBot):
    """
    Backtesting bot for strategy validation and optimization
    """
    
    def __init__(self, strategy: BaseStrategy, config: Dict[str, Any]):
        super().__init__(strategy, config)
        self.performance_analyzer = PerformanceAnalyzer()
        self.backtest_results = {}
        self.trades_history = []
        self.equity_curve = []
        self.initial_capital = config.get('initial_capital', 10000.0)
        self.current_capital = self.initial_capital
        self.position_size = 0
        self.current_position = None
        self.commission_rate = config.get('commission_rate', 0.001)  # 0.1%
        
    def run_backtest(self, data: pd.DataFrame, start_date: Optional[str] = None, 
                     end_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Run backtest on historical data
        
        Args:
            data: Historical OHLCV data
            start_date: Start date for backtest (optional)
            end_date: End date for backtest (optional)
        
        Returns:
            Dictionary with backtest results
        """
        try:
            logger.info(f"Starting backtest for {self.strategy.__class__.__name__}")
            
            # Validate data
            DataValidator.validate_ohlcv_data(data)
            
            # Filter data by date range if specified
            if start_date:
                data = data[data.index >= pd.to_datetime(start_date)]
            if end_date:
                data = data[data.index <= pd.to_datetime(end_date)]
            
            if len(data) < 50:  # Need sufficient data for indicators
                raise ValueError("Insufficient data for backtesting")
            
            # Initialize
            self.current_capital = self.initial_capital
            self.position_size = 0
            self.current_position = None
            self.trades_history = []
            self.equity_curve = []
            
            # Process each data point
            for i in range(len(data)):
                current_data = data.iloc[:i+1]  # Data up to current point
                timestamp = data.index[i]
                current_price = data.iloc[i]['close']
                
                # Skip if insufficient data for strategy
                if len(current_data) < 30:
                    self._update_equity(timestamp, current_price)
                    continue
                
                # Generate signal
                signal = self.strategy.generate_signal(current_data)
                
                if signal and signal.action != 'hold':
                    self._execute_backtest_trade(signal, timestamp, current_price)
                
                self._update_equity(timestamp, current_price)
            
            # Close any open position at the end
            if self.current_position:
                final_price = data.iloc[-1]['close']
                final_timestamp = data.index[-1]
                self._close_position(final_timestamp, final_price, "End of backtest")
            
            # Calculate performance metrics
            self.backtest_results = self._calculate_backtest_results()
            
            logger.info(f"Backtest completed. Total return: {self.backtest_results.get('total_return', 0):.2%}")
            
            return self.backtest_results
            
        except Exception as e:
            logger.error(f"Error during backtesting: {e}")
            return {'error': str(e)}
    
    def _execute_backtest_trade(self, signal, timestamp: datetime, price: float):
        """Execute a trade in backtest mode"""
        try:
            if signal.action == 'buy' and not self.current_position:
                # Open long position
                commission = self.current_capital * self.commission_rate
                position_value = self.current_capital - commission
                quantity = position_value / price
                
                self.current_position = {
                    'type': 'long',
                    'entry_price': price,
                    'entry_time': timestamp,
                    'quantity': quantity,
                    'entry_value': position_value
                }
                
                self.position_size = quantity
                self.current_capital = 0  # All capital in position
                
                # Record trade
                trade = {
                    'timestamp': timestamp,
                    'action': 'buy',
                    'price': price,
                    'quantity': quantity,
                    'commission': commission,
                    'signal_strength': signal.confidence
                }
                self.trades_history.append(trade)
                
                logger.debug(f"Opened long position: {quantity:.6f} @ {price:.2f}")
                
            elif signal.action == 'sell' and self.current_position and self.current_position['type'] == 'long':
                # Close long position
                self._close_position(timestamp, price, "Sell signal")
                
        except Exception as e:
            logger.error(f"Error executing backtest trade: {e}")
    
    def _close_position(self, timestamp: datetime, price: float, reason: str):
        """Close current position"""
        if not self.current_position:
            return
        
        try:
            quantity = self.current_position['quantity']
            entry_price = self.current_position['entry_price']
            
            # Calculate P&L
            exit_value = quantity * price
            commission = exit_value * self.commission_rate
            net_exit_value = exit_value - commission
            
            entry_value = self.current_position['entry_value']
            pnl = net_exit_value - entry_value
            pnl_percent = pnl / entry_value
            
            self.current_capital = net_exit_value
            
            # Record trade
            trade = {
                'timestamp': timestamp,
                'action': 'sell',
                'price': price,
                'quantity': quantity,
                'commission': commission,
                'pnl': pnl,
                'pnl_percent': pnl_percent,
                'hold_time': timestamp - self.current_position['entry_time'],
                'entry_price': entry_price,
                'exit_reason': reason
            }
            self.trades_history.append(trade)
            
            # Add to performance analyzer
            self.performance_analyzer.add_trade({
                'timestamp': timestamp,
                'symbol': self.config.get('symbol', 'UNKNOWN'),
                'side': 'sell',
                'quantity': quantity,
                'price': price,
                'profit': pnl
            })
            
            logger.debug(f"Closed position: {quantity:.6f} @ {price:.2f}, P&L: {pnl:.2f} ({pnl_percent:.2%})")
            
            self.current_position = None
            self.position_size = 0
            
        except Exception as e:
            logger.error(f"Error closing position: {e}")
    
    def _update_equity(self, timestamp: datetime, price: float):
        """Update equity curve"""
        if self.current_position:
            # Calculate current position value
            position_value = self.current_position['quantity'] * price
            total_equity = position_value
        else:
            total_equity = self.current_capital
        
        self.equity_curve.append({
            'timestamp': timestamp,
            'equity': total_equity,
            'price': price
        })
        
        # Add to performance analyzer
        self.performance_analyzer.add_portfolio_snapshot({
            'timestamp': timestamp,
            'equity': total_equity,
            'cash': self.current_capital,
            'position_value': total_equity - self.current_capital
        })
    
    def _calculate_backtest_results(self) -> Dict[str, Any]:
        """Calculate comprehensive backtest results"""
        if not self.equity_curve:
            return {}
        
        equity_df = pd.DataFrame(self.equity_curve)
        equity_df.set_index('timestamp', inplace=True)
        
        # Basic metrics
        initial_equity = self.initial_capital
        final_equity = equity_df['equity'].iloc[-1]
        total_return = (final_equity - initial_equity) / initial_equity
        
        # Calculate returns series
        returns = equity_df['equity'].pct_change().dropna()
        
        # Performance metrics from analyzer
        performance_report = self.performance_analyzer.generate_performance_report()
        
        # Additional backtest-specific metrics
        results = {
            'initial_capital': initial_equity,
            'final_equity': final_equity,
            'total_return': total_return,
            'total_trades': len([t for t in self.trades_history if t['action'] == 'sell']),
            'winning_trades': len([t for t in self.trades_history if t.get('pnl', 0) > 0]),
            'losing_trades': len([t for t in self.trades_history if t.get('pnl', 0) < 0]),
            'avg_trade_return': np.mean([t.get('pnl_percent', 0) for t in self.trades_history if 'pnl_percent' in t]),
            'max_drawdown': self._calculate_max_drawdown(equity_df['equity']),
            'sharpe_ratio': self._calculate_sharpe_ratio(returns),
            'equity_curve': equity_df.to_dict('records'),
            'trades_history': self.trades_history
        }
        
        # Merge with performance analyzer results
        results.update(performance_report)
        
        return results
    
    def _calculate_max_drawdown(self, equity_series: pd.Series) -> float:
        """Calculate maximum drawdown"""
        running_max = equity_series.expanding().max()
        drawdown = (equity_series - running_max) / running_max
        return abs(drawdown.min())
    
    def _calculate_sharpe_ratio(self, returns: pd.Series, risk_free_rate: float = 0.02) -> float:
        """Calculate Sharpe ratio"""
        if len(returns) == 0 or returns.std() == 0:
            return 0.0
        
        excess_returns = returns - (risk_free_rate / 252)  # Daily risk-free rate
        return np.sqrt(252) * excess_returns.mean() / returns.std()
    
    def get_trades_dataframe(self) -> pd.DataFrame:
        """Get trades as DataFrame"""
        return pd.DataFrame(self.trades_history)
    
    def get_equity_curve_dataframe(self) -> pd.DataFrame:
        """Get equity curve as DataFrame"""
        return pd.DataFrame(self.equity_curve)
    
    def plot_results(self):
        """Plot backtest results (placeholder for future implementation)"""
        logger.info("Plotting functionality will be implemented in future versions")
        pass
    
    async def start(self) -> bool:
        """Start method (not used for backtesting)"""
        logger.warning("Backtesting bot does not support start() method")
        return False
    
    async def stop(self) -> bool:
        """Stop method (not used for backtesting)"""
        logger.warning("Backtesting bot does not support stop() method")
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """Get backtest bot status"""
        return {
            'type': 'backtesting',
            'strategy': self.strategy.__class__.__name__,
            'status': 'ready',
            'total_trades': len(self.trades_history),
            'current_capital': self.current_capital,
            'initial_capital': self.initial_capital,
            'has_results': bool(self.backtest_results)
        }
