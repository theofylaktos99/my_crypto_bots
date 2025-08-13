# performance_analyzer.py - Performance Analysis Utilities
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class PerformanceAnalyzer:
    """Performance analysis utilities for trading systems"""
    
    def __init__(self):
        self.trades = []
        self.portfolio_history = []
        
    def add_trade(self, trade_data: Dict[str, Any]) -> None:
        """Add a trade to the performance tracking"""
        required_fields = ['timestamp', 'symbol', 'side', 'quantity', 'price']
        if all(field in trade_data for field in required_fields):
            trade_data['timestamp'] = pd.to_datetime(trade_data['timestamp'])
            self.trades.append(trade_data)
        else:
            logger.warning(f"Trade data missing required fields: {trade_data}")
    
    def add_portfolio_snapshot(self, portfolio_data: Dict[str, Any]) -> None:
        """Add a portfolio snapshot for tracking"""
        portfolio_data['timestamp'] = pd.to_datetime(portfolio_data.get('timestamp', datetime.now()))
        self.portfolio_history.append(portfolio_data)
    
    def calculate_returns(self, prices: pd.Series) -> pd.Series:
        """Calculate returns from price series"""
        return prices.pct_change().dropna()
    
    def calculate_sharpe_ratio(self, returns: pd.Series, risk_free_rate: float = 0.02) -> float:
        """
        Calculate Sharpe ratio
        
        Args:
            returns: Series of returns
            risk_free_rate: Annual risk-free rate (default 2%)
        
        Returns:
            Sharpe ratio
        """
        if len(returns) == 0 or returns.std() == 0:
            return 0.0
        
        excess_returns = returns - (risk_free_rate / 252)  # Daily risk-free rate
        return np.sqrt(252) * excess_returns.mean() / returns.std()
    
    def calculate_max_drawdown(self, equity_curve: pd.Series) -> Tuple[float, datetime, datetime]:
        """
        Calculate maximum drawdown
        
        Returns:
            (max_drawdown_percent, start_date, end_date)
        """
        if len(equity_curve) == 0:
            return 0.0, None, None
        
        # Calculate running maximum
        running_max = equity_curve.expanding().max()
        drawdown = (equity_curve - running_max) / running_max
        
        max_drawdown = drawdown.min()
        max_dd_date = drawdown.idxmin()
        
        # Find start of drawdown period
        start_date = running_max[:max_dd_date].idxmax()
        
        return abs(max_drawdown), start_date, max_dd_date
    
    def calculate_volatility(self, returns: pd.Series, annualize: bool = True) -> float:
        """Calculate volatility (standard deviation of returns)"""
        if len(returns) == 0:
            return 0.0
        
        vol = returns.std()
        if annualize:
            vol *= np.sqrt(252)  # Annualize assuming 252 trading days
        
        return vol
    
    def calculate_win_rate(self) -> float:
        """Calculate win rate from trades"""
        if not self.trades:
            return 0.0
        
        profitable_trades = 0
        for trade in self.trades:
            if trade.get('profit', 0) > 0:
                profitable_trades += 1
        
        return profitable_trades / len(self.trades)
    
    def calculate_profit_factor(self) -> float:
        """Calculate profit factor (gross profits / gross losses)"""
        if not self.trades:
            return 0.0
        
        gross_profits = sum(trade.get('profit', 0) for trade in self.trades if trade.get('profit', 0) > 0)
        gross_losses = abs(sum(trade.get('profit', 0) for trade in self.trades if trade.get('profit', 0) < 0))
        
        if gross_losses == 0:
            return float('inf') if gross_profits > 0 else 0.0
        
        return gross_profits / gross_losses
    
    def calculate_average_trade(self) -> Dict[str, float]:
        """Calculate average trade statistics"""
        if not self.trades:
            return {'avg_profit': 0.0, 'avg_win': 0.0, 'avg_loss': 0.0}
        
        profits = [trade.get('profit', 0) for trade in self.trades]
        wins = [p for p in profits if p > 0]
        losses = [p for p in profits if p < 0]
        
        return {
            'avg_profit': np.mean(profits) if profits else 0.0,
            'avg_win': np.mean(wins) if wins else 0.0,
            'avg_loss': np.mean(losses) if losses else 0.0
        }
    
    def calculate_var(self, returns: pd.Series, confidence_level: float = 0.05) -> float:
        """
        Calculate Value at Risk (VaR)
        
        Args:
            returns: Series of returns
            confidence_level: Confidence level (default 5% = 95% VaR)
        
        Returns:
            VaR value
        """
        if len(returns) == 0:
            return 0.0
        
        return np.percentile(returns, confidence_level * 100)
    
    def calculate_calmar_ratio(self, returns: pd.Series) -> float:
        """Calculate Calmar ratio (annual return / max drawdown)"""
        if len(returns) == 0:
            return 0.0
        
        annual_return = (1 + returns.mean()) ** 252 - 1
        equity_curve = (1 + returns).cumprod()
        max_drawdown, _, _ = self.calculate_max_drawdown(equity_curve)
        
        if max_drawdown == 0:
            return float('inf') if annual_return > 0 else 0.0
        
        return annual_return / max_drawdown
    
    def generate_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        if not self.trades and not self.portfolio_history:
            return {'error': 'No data available for performance analysis'}
        
        report = {}
        
        # Trade statistics
        if self.trades:
            report['total_trades'] = len(self.trades)
            report['win_rate'] = self.calculate_win_rate()
            report['profit_factor'] = self.calculate_profit_factor()
            report['average_trades'] = self.calculate_average_trade()
            
            # Total P&L
            total_pnl = sum(trade.get('profit', 0) for trade in self.trades)
            report['total_pnl'] = total_pnl
        
        # Portfolio performance
        if self.portfolio_history:
            portfolio_df = pd.DataFrame(self.portfolio_history)
            if 'equity' in portfolio_df.columns:
                equity_series = portfolio_df.set_index('timestamp')['equity']
                returns = self.calculate_returns(equity_series)
                
                report['sharpe_ratio'] = self.calculate_sharpe_ratio(returns)
                report['volatility'] = self.calculate_volatility(returns)
                report['max_drawdown'], report['dd_start'], report['dd_end'] = self.calculate_max_drawdown(equity_series)
                report['calmar_ratio'] = self.calculate_calmar_ratio(returns)
                report['var_5'] = self.calculate_var(returns)
                
                # Total return
                if len(equity_series) > 1:
                    report['total_return'] = (equity_series.iloc[-1] / equity_series.iloc[0]) - 1
                    report['annual_return'] = (1 + report['total_return']) ** (252 / len(equity_series)) - 1
        
        return report
    
    def get_trades_dataframe(self) -> pd.DataFrame:
        """Get trades as DataFrame"""
        if not self.trades:
            return pd.DataFrame()
        
        return pd.DataFrame(self.trades)
    
    def get_portfolio_dataframe(self) -> pd.DataFrame:
        """Get portfolio history as DataFrame"""
        if not self.portfolio_history:
            return pd.DataFrame()
        
        return pd.DataFrame(self.portfolio_history)
    
    def reset_data(self) -> None:
        """Reset all performance data"""
        self.trades = []
        self.portfolio_history = []
        logger.info("Performance data reset")
    
    @staticmethod
    def calculate_benchmark_comparison(strategy_returns: pd.Series, benchmark_returns: pd.Series) -> Dict[str, float]:
        """
        Compare strategy performance against benchmark
        
        Args:
            strategy_returns: Strategy returns
            benchmark_returns: Benchmark returns (e.g., market index)
        
        Returns:
            Comparison metrics
        """
        if len(strategy_returns) == 0 or len(benchmark_returns) == 0:
            return {}
        
        # Align series by index
        aligned_strategy, aligned_benchmark = strategy_returns.align(benchmark_returns, join='inner')
        
        if len(aligned_strategy) == 0:
            return {}
        
        # Calculate metrics
        strategy_total = (1 + aligned_strategy).cumprod().iloc[-1] - 1
        benchmark_total = (1 + aligned_benchmark).cumprod().iloc[-1] - 1
        
        excess_returns = aligned_strategy - aligned_benchmark
        tracking_error = excess_returns.std() * np.sqrt(252)
        
        return {
            'strategy_return': strategy_total,
            'benchmark_return': benchmark_total,
            'excess_return': strategy_total - benchmark_total,
            'tracking_error': tracking_error,
            'information_ratio': excess_returns.mean() * np.sqrt(252) / tracking_error if tracking_error != 0 else 0,
            'beta': np.cov(aligned_strategy, aligned_benchmark)[0, 1] / np.var(aligned_benchmark) if np.var(aligned_benchmark) != 0 else 0
        }
