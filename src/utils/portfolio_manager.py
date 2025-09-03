# portfolio_manager.py - Advanced Portfolio Management System
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
import json
import os

logger = logging.getLogger(__name__)

class PortfolioManager:
    """Advanced Portfolio Management with Risk Controls"""
    
    def __init__(self, initial_balance: float = 10000.0):
        self.initial_balance = initial_balance
        self.current_balance = initial_balance
        self.positions = {}
        self.trade_history = []
        self.daily_stats = {}
        
        # Risk management parameters
        self.max_risk_per_trade = 0.02  # 2% max risk per trade
        self.max_portfolio_risk = 0.06  # 6% max total portfolio risk
        self.max_drawdown_limit = 0.15  # 15% max drawdown before stop
        self.max_positions = 3  # Max simultaneous positions
        
        # Performance tracking
        self.peak_balance = initial_balance
        self.current_drawdown = 0.0
        self.total_trades = 0
        self.winning_trades = 0
        
        self.portfolio_file = f"portfolio_state_{datetime.now().strftime('%Y%m%d')}.json"
        self._load_portfolio_state()
    
    def _load_portfolio_state(self):
        """Load portfolio state from file"""
        try:
            if os.path.exists(self.portfolio_file):
                with open(self.portfolio_file, 'r') as f:
                    data = json.load(f)
                    self.current_balance = data.get('current_balance', self.initial_balance)
                    self.positions = data.get('positions', {})
                    self.trade_history = data.get('trade_history', [])
                    self.peak_balance = data.get('peak_balance', self.initial_balance)
                    self.total_trades = data.get('total_trades', 0)
                    self.winning_trades = data.get('winning_trades', 0)
                    logger.info("Portfolio state loaded from file")
        except Exception as e:
            logger.warning(f"Could not load portfolio state: {e}")
    
    def _save_portfolio_state(self):
        """Save portfolio state to file"""
        try:
            data = {
                'current_balance': self.current_balance,
                'positions': self.positions,
                'trade_history': self.trade_history[-100:],  # Keep last 100 trades
                'peak_balance': self.peak_balance,
                'total_trades': self.total_trades,
                'winning_trades': self.winning_trades,
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.portfolio_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Could not save portfolio state: {e}")
    
    def calculate_position_size(self, symbol: str, entry_price: float, 
                               stop_loss_price: float) -> float:
        """Calculate optimal position size based on risk management"""
        try:
            # Calculate risk per share
            risk_per_share = abs(entry_price - stop_loss_price)
            
            if risk_per_share <= 0:
                logger.warning("Invalid risk calculation - using fallback")
                return self.current_balance * 0.01 / entry_price  # 1% fallback
            
            # Calculate maximum risk amount
            max_risk_amount = self.current_balance * self.max_risk_per_trade
            
            # Calculate position size
            position_size = max_risk_amount / risk_per_share
            
            # Apply portfolio constraints
            max_position_value = self.current_balance * 0.3  # Max 30% per position
            max_size_by_value = max_position_value / entry_price
            
            position_size = min(position_size, max_size_by_value)
            
            # Check if we can afford the position
            position_value = position_size * entry_price
            if position_value > self.current_balance * 0.95:  # Leave 5% buffer
                position_size = (self.current_balance * 0.95) / entry_price
            
            logger.info(f"Position size calculated: {position_size:.6f} {symbol.split('/')[0]}")
            logger.info(f"Position value: ${position_value:.2f}")
            logger.info(f"Risk amount: ${max_risk_amount:.2f}")
            
            return position_size
            
        except Exception as e:
            logger.error(f"Position size calculation error: {e}")
            return self.current_balance * 0.01 / entry_price  # Conservative fallback
    
    def can_open_position(self, symbol: str, position_size: float, entry_price: float) -> bool:
        """Check if we can open a new position"""
        try:
            # Check maximum number of positions
            if len(self.positions) >= self.max_positions:
                logger.info(f"Cannot open position: max positions ({self.max_positions}) reached")
                return False
            
            # Check available balance
            position_value = position_size * entry_price
            if position_value > self.current_balance * 0.95:
                logger.info("Cannot open position: insufficient balance")
                return False
            
            # Check portfolio risk limit
            current_portfolio_risk = self._calculate_portfolio_risk()
            if current_portfolio_risk > self.max_portfolio_risk:
                logger.info(f"Cannot open position: portfolio risk too high ({current_portfolio_risk:.1%})")
                return False
            
            # Check drawdown limit
            if self.current_drawdown > self.max_drawdown_limit:
                logger.info(f"Cannot open position: drawdown limit exceeded ({self.current_drawdown:.1%})")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Position check error: {e}")
            return False
    
    def open_position(self, symbol: str, amount: float, entry_price: float,
                     stop_loss_price: float, take_profit_price: Optional[float] = None) -> str:
        """Open a new position"""
        try:
            if not self.can_open_position(symbol, amount, entry_price):
                return None
            
            position_id = f"{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            position_value = amount * entry_price
            
            position = {
                'symbol': symbol,
                'amount': amount,
                'entry_price': entry_price,
                'entry_time': datetime.now().isoformat(),
                'stop_loss_price': stop_loss_price,
                'take_profit_price': take_profit_price,
                'position_value': position_value,
                'unrealized_pnl': 0.0,
                'status': 'open'
            }
            
            self.positions[position_id] = position
            self.current_balance -= position_value  # Update available balance
            
            # Log the trade
            trade_log = {
                'position_id': position_id,
                'action': 'OPEN',
                'symbol': symbol,
                'amount': amount,
                'price': entry_price,
                'timestamp': datetime.now().isoformat(),
                'balance_after': self.current_balance
            }
            self.trade_history.append(trade_log)
            
            self._save_portfolio_state()
            
            logger.info(f"Position opened: {position_id}")
            logger.info(f"Available balance: ${self.current_balance:.2f}")
            
            return position_id
            
        except Exception as e:
            logger.error(f"Error opening position: {e}")
            return None
    
    def close_position(self, position_id: str, exit_price: float, 
                      reason: str = "MANUAL") -> Dict[str, Any]:
        """Close an existing position"""
        try:
            if position_id not in self.positions:
                logger.error(f"Position not found: {position_id}")
                return None
            
            position = self.positions[position_id]
            
            # Calculate PnL
            pnl_amount = (exit_price - position['entry_price']) * position['amount']
            pnl_percent = ((exit_price - position['entry_price']) / position['entry_price']) * 100
            
            # Update balance
            exit_value = position['amount'] * exit_price
            self.current_balance += exit_value
            
            # Update position
            position['exit_price'] = exit_price
            position['exit_time'] = datetime.now().isoformat()
            position['pnl_amount'] = pnl_amount
            position['pnl_percent'] = pnl_percent
            position['status'] = 'closed'
            position['close_reason'] = reason
            
            # Update statistics
            self.total_trades += 1
            if pnl_amount > 0:
                self.winning_trades += 1
            
            # Update peak balance and drawdown
            if self.current_balance > self.peak_balance:
                self.peak_balance = self.current_balance
                self.current_drawdown = 0.0
            else:
                self.current_drawdown = (self.peak_balance - self.current_balance) / self.peak_balance
            
            # Log the trade
            trade_log = {
                'position_id': position_id,
                'action': 'CLOSE',
                'symbol': position['symbol'],
                'amount': position['amount'],
                'entry_price': position['entry_price'],
                'exit_price': exit_price,
                'pnl_amount': pnl_amount,
                'pnl_percent': pnl_percent,
                'timestamp': datetime.now().isoformat(),
                'balance_after': self.current_balance,
                'reason': reason
            }
            self.trade_history.append(trade_log)
            
            # Remove from active positions
            del self.positions[position_id]
            
            self._save_portfolio_state()
            
            logger.info(f"Position closed: {position_id}")
            logger.info(f"PnL: ${pnl_amount:.2f} ({pnl_percent:.2f}%)")
            logger.info(f"New balance: ${self.current_balance:.2f}")
            
            return {
                'position_id': position_id,
                'pnl_amount': pnl_amount,
                'pnl_percent': pnl_percent,
                'exit_price': exit_price
            }
            
        except Exception as e:
            logger.error(f"Error closing position: {e}")
            return None
    
    def update_position_prices(self, current_prices: Dict[str, float]):
        """Update unrealized PnL for all open positions"""
        try:
            for position_id, position in self.positions.items():
                symbol = position['symbol']
                if symbol in current_prices:
                    current_price = current_prices[symbol]
                    unrealized_pnl = (current_price - position['entry_price']) * position['amount']
                    position['unrealized_pnl'] = unrealized_pnl
                    position['current_price'] = current_price
            
            self._save_portfolio_state()
            
        except Exception as e:
            logger.error(f"Error updating position prices: {e}")
    
    def _calculate_portfolio_risk(self) -> float:
        """Calculate current portfolio risk exposure"""
        try:
            if not self.positions:
                return 0.0
            
            total_risk = 0.0
            for position in self.positions.values():
                # Calculate risk as potential loss to stop loss
                risk_per_share = abs(position['entry_price'] - position['stop_loss_price'])
                position_risk = risk_per_share * position['amount']
                total_risk += position_risk
            
            return total_risk / self.initial_balance
            
        except Exception as e:
            logger.error(f"Portfolio risk calculation error: {e}")
            return 0.0
    
    def get_portfolio_summary(self) -> Dict[str, Any]:
        """Get comprehensive portfolio summary"""
        try:
            # Calculate totals
            total_position_value = sum(
                pos['amount'] * pos.get('current_price', pos['entry_price']) 
                for pos in self.positions.values()
            )
            
            total_unrealized_pnl = sum(
                pos.get('unrealized_pnl', 0) 
                for pos in self.positions.values()
            )
            
            total_portfolio_value = self.current_balance + total_position_value
            
            # Calculate returns
            total_return = ((total_portfolio_value - self.initial_balance) / self.initial_balance) * 100
            
            # Calculate win rate
            win_rate = (self.winning_trades / self.total_trades * 100) if self.total_trades > 0 else 0
            
            # Calculate recent performance (last 30 days)
            recent_trades = [
                trade for trade in self.trade_history
                if 'timestamp' in trade and 
                datetime.fromisoformat(trade['timestamp']) > datetime.now() - timedelta(days=30)
            ]
            
            return {
                'initial_balance': self.initial_balance,
                'current_balance': self.current_balance,
                'total_position_value': total_position_value,
                'total_portfolio_value': total_portfolio_value,
                'total_return_percent': total_return,
                'unrealized_pnl': total_unrealized_pnl,
                'peak_balance': self.peak_balance,
                'current_drawdown_percent': self.current_drawdown * 100,
                'total_trades': self.total_trades,
                'winning_trades': self.winning_trades,
                'win_rate_percent': win_rate,
                'active_positions': len(self.positions),
                'portfolio_risk_percent': self._calculate_portfolio_risk() * 100,
                'recent_trades_30d': len(recent_trades),
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Portfolio summary error: {e}")
            return {}
    
    def get_performance_report(self) -> str:
        """Generate a formatted performance report"""
        summary = self.get_portfolio_summary()
        
        if not summary:
            return "Could not generate performance report"
        
        report = f"""
╔══════════════════════════════════════════════════════════════╗
║                    PORTFOLIO PERFORMANCE REPORT             ║
╠══════════════════════════════════════════════════════════════╣
║  💰 Balance Information                                      ║
║     Initial Balance:     ${summary['initial_balance']:>10.2f}     ║
║     Current Balance:     ${summary['current_balance']:>10.2f}     ║
║     Position Value:      ${summary['total_position_value']:>10.2f}     ║
║     Total Portfolio:     ${summary['total_portfolio_value']:>10.2f}     ║
║                                                              ║
║  📈 Performance Metrics                                      ║
║     Total Return:        {summary['total_return_percent']:>9.2f}%      ║
║     Unrealized P&L:      ${summary['unrealized_pnl']:>10.2f}     ║
║     Peak Balance:        ${summary['peak_balance']:>10.2f}     ║
║     Current Drawdown:    {summary['current_drawdown_percent']:>9.2f}%      ║
║                                                              ║
║  📊 Trading Statistics                                       ║
║     Total Trades:        {summary['total_trades']:>14}       ║
║     Winning Trades:      {summary['winning_trades']:>14}       ║
║     Win Rate:            {summary['win_rate_percent']:>9.1f}%      ║
║     Active Positions:    {summary['active_positions']:>14}       ║
║                                                              ║
║  ⚠️  Risk Management                                          ║
║     Portfolio Risk:      {summary['portfolio_risk_percent']:>9.2f}%      ║
║     Recent Trades (30d): {summary['recent_trades_30d']:>14}       ║
║                                                              ║
║  🕒 Last Updated: {summary['last_updated'][:19]}            ║
╚══════════════════════════════════════════════════════════════╝
        """
        
        return report.strip()

# Global portfolio manager instance
portfolio_manager = PortfolioManager()

def get_portfolio_manager():
    """Get the global portfolio manager instance"""
    return portfolio_manager

if __name__ == "__main__":
    # Test the portfolio manager
    pm = PortfolioManager(10000)
    
    print("Portfolio Manager initialized")
    print(pm.get_performance_report())
    
    # Simulate some trades
    pos_id = pm.open_position("BTC/USDT", 0.1, 45000, 44000, 47000)
    if pos_id:
        print(f"\\nOpened position: {pos_id}")
        
        # Update prices
        pm.update_position_prices({"BTC/USDT": 46000})
        print("\\nAfter price update:")
        print(pm.get_performance_report())
        
        # Close position
        result = pm.close_position(pos_id, 46500, "TAKE_PROFIT")
        if result:
            print(f"\\nClosed position with PnL: ${result['pnl_amount']:.2f}")
            print("\\nFinal report:")
            print(pm.get_performance_report())
