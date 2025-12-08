# live_trading_bot.py - Live Trading Bot Implementation
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta
import logging
from typing import Dict, Any, Optional
import asyncio
import threading

from .base_bot import BaseBot
from ..api.market_data import MarketDataFetcher
from ..api.binance_client import BinanceClient
from ..strategies.base_strategy import BaseStrategy
from ..utils.config_manager import SecurityConfig as ConfigManager

logger = logging.getLogger(__name__)

class LiveTradingBot(BaseBot):
    """Live trading bot implementation"""
    
    def __init__(self, name: str, symbol: str, timeframe: str, 
                 strategy: BaseStrategy, config_manager: ConfigManager):
        super().__init__(name, symbol, timeframe)
        
        self.strategy = strategy
        self.config_manager = config_manager
        self.market_data_fetcher = MarketDataFetcher()
        self.exchange_client = None
        
        # Trading state
        self.current_data = pd.DataFrame()
        self.last_signal = 'hold'
        self.last_price = 0.0
        self.position_size = 0.0
        
        # Performance tracking
        self.trades_today = 0
        self.daily_pnl = 0.0
        self.last_trade_time = None
        
        logger.info(f"Initialized LiveTradingBot: {name}")
    
    def initialize(self) -> bool:
        """Initialize bot components"""
        try:
            logger.info(f"Initializing {self.name}...")
            
            # Initialize exchange client
            exchange_config = self.config_manager.get_exchange_config()
            
            if exchange_config.get('api_key') and exchange_config.get('api_secret'):
                self.exchange_client = BinanceClient(
                    api_key=exchange_config['api_key'],
                    api_secret=exchange_config['api_secret'],
                    sandbox=exchange_config.get('sandbox_mode', True)
                )
                
                if not self.exchange_client.connect():
                    logger.error(f"Failed to connect to exchange for {self.name}")
                    return False
            else:
                logger.warning(f"No API credentials found for {self.name} - running in simulation mode")
            
            # Load historical data for strategy initialization
            self._load_initial_data()
            
            # Validate strategy
            if not self.strategy.validate_data(self.current_data):
                logger.error(f"Strategy validation failed for {self.name}")
                return False
            
            logger.info(f"✅ {self.name} initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error initializing {self.name}: {e}")
            return False
    
    def run_cycle(self) -> bool:
        """Execute one trading cycle"""
        try:
            # Check if markets are open (basic check)
            if not self._are_markets_open():
                logger.debug(f"{self.name}: Markets closed, skipping cycle")
                return True
            
            # Fetch latest market data
            if not self._update_market_data():
                logger.warning(f"{self.name}: Failed to update market data")
                return False
            
            # Generate trading signal
            signal = self.strategy.generate_signal(self.current_data)
            
            if signal != self.last_signal:
                logger.info(f"{self.name}: New signal: {signal} (was: {self.last_signal})")
                self.last_signal = signal
            
            # Execute trading logic
            if signal != 'hold':
                success = self._execute_signal(signal)
                if not success:
                    logger.warning(f"{self.name}: Failed to execute signal: {signal}")
                    return False
            
            # Update bot statistics
            self._update_statistics()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error in trading cycle for {self.name}: {e}")
            self.last_error = str(e)
            return False
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            logger.info(f"Cleaning up {self.name}...")
            
            # Close any open positions (if in real trading mode)
            if self.exchange_client and self.strategy.position != 0:
                self._close_all_positions()
            
            # Save final statistics
            self._save_performance_data()
            
            logger.info(f"✅ {self.name} cleanup complete")
            
        except Exception as e:
            logger.error(f"❌ Error during cleanup for {self.name}: {e}")
    
    def _load_initial_data(self):
        """Load initial historical data for strategy"""
        try:
            # For testing, we'll use basic market data
            # In production, you'd load proper OHLCV data
            base_symbol = self.symbol.split('/')[0]  # BTC from BTC/USDT
            
            # Create sample OHLCV data for testing
            dates = pd.date_range(
                start=datetime.now() - timedelta(days=30),
                end=datetime.now(),
                freq='1H'
            )
            
            # Generate realistic sample data
            np.random.seed(42)  # For reproducible testing
            base_price = 45000 if base_symbol == 'BTC' else 3000
            
            prices = []
            current_price = base_price
            
            for i in range(len(dates)):
                # Add some realistic price movement
                change = np.random.normal(0, 0.02)  # 2% volatility
                current_price *= (1 + change)
                prices.append(current_price)
            
            # Create OHLCV data
            self.current_data = pd.DataFrame({
                'timestamp': dates,
                'open': prices,
                'high': [p * (1 + abs(np.random.normal(0, 0.01))) for p in prices],
                'low': [p * (1 - abs(np.random.normal(0, 0.01))) for p in prices],
                'close': prices,
                'volume': [np.random.uniform(100, 1000) for _ in prices]
            })
            
            self.current_data.set_index('timestamp', inplace=True)
            self.last_price = self.current_data['close'].iloc[-1]
            
            logger.info(f"Loaded {len(self.current_data)} data points for {self.name}")
            
        except Exception as e:
            logger.error(f"Error loading initial data for {self.name}: {e}")
            # Create minimal fallback data
            self.current_data = pd.DataFrame({
                'open': [45000], 'high': [45500], 'low': [44500], 
                'close': [45234], 'volume': [500]
            })
    
    def _update_market_data(self) -> bool:
        """Update market data with latest prices"""
        try:
            # Get latest market data
            market_data = self.market_data_fetcher.get_live_market_data(5)
            
            if not market_data:
                return False
            
            # Extract price for our symbol
            base_symbol = self.symbol.split('/')[0]  # BTC from BTC/USDT
            
            if base_symbol in market_data:
                latest_price = market_data[base_symbol]['price']
                
                # Add new row to our data
                new_row = pd.DataFrame({
                    'open': [self.last_price],
                    'high': [max(self.last_price, latest_price)],
                    'low': [min(self.last_price, latest_price)],
                    'close': [latest_price],
                    'volume': [np.random.uniform(100, 1000)]  # Placeholder volume
                }, index=[datetime.now()])
                
                # Append to existing data
                self.current_data = pd.concat([self.current_data, new_row])
                
                # Keep only last 1000 rows to prevent memory issues
                if len(self.current_data) > 1000:
                    self.current_data = self.current_data.tail(1000)
                
                self.last_price = latest_price
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error updating market data for {self.name}: {e}")
            return False
    
    def _execute_signal(self, signal: str) -> bool:
        """Execute trading signal"""
        try:
            current_price = self.last_price
            
            # Check daily limits
            if not self._check_trading_limits():
                return False
            
            # Simulate trade execution
            if signal in ['buy', 'sell']:
                # Calculate position size
                account_balance = 10000  # Simulated balance
                risk_amount = account_balance * self.risk_config.get('risk_per_trade', 0.02)
                
                # Simulate position size calculation
                self.position_size = risk_amount / current_price
                
                # Log the trade
                self.log_trade(
                    action=signal.upper(),
                    price=current_price,
                    quantity=self.position_size,
                    reason=f"Strategy signal: {signal}"
                )
                
                # Update strategy position
                self.strategy.update_position(signal, current_price)
                
                # Update counters
                self.trades_today += 1
                self.last_trade_time = datetime.now()
                
                return True
            
            elif signal in ['close_long', 'close_short']:
                if self.strategy.position != 0:
                    # Calculate P&L
                    if self.strategy.position > 0:  # Long position
                        pnl = (current_price - self.strategy.entry_price) / self.strategy.entry_price * 100
                    else:  # Short position
                        pnl = (self.strategy.entry_price - current_price) / self.strategy.entry_price * 100
                    
                    # Log the close
                    self.log_trade(
                        action="CLOSE",
                        price=current_price,
                        quantity=self.position_size,
                        pnl=pnl,
                        reason=f"Strategy signal: {signal}"
                    )
                    
                    # Update strategy
                    self.strategy.close_position(current_price, datetime.now(), signal)
                    
                    # Update daily P&L
                    self.daily_pnl += pnl
                    
                    return True
            
            return True
            
        except Exception as e:
            logger.error(f"Error executing signal {signal} for {self.name}: {e}")
            return False
    
    def _check_trading_limits(self) -> bool:
        """Check if trading limits allow new trades"""
        try:
            risk_config = self.config_manager.get_risk_config()
            
            # Check daily trade limit
            max_daily_trades = risk_config.get('max_daily_trades', 10)
            if self.trades_today >= max_daily_trades:
                logger.warning(f"{self.name}: Daily trade limit reached ({max_daily_trades})")
                return False
            
            # Check daily loss limit
            max_daily_loss = risk_config.get('max_daily_loss', 0.05) * 100  # Convert to percentage
            if self.daily_pnl <= -max_daily_loss:
                logger.warning(f"{self.name}: Daily loss limit reached ({max_daily_loss}%)")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking trading limits for {self.name}: {e}")
            return True  # Allow trading if check fails
    
    def _are_markets_open(self) -> bool:
        """Check if markets are open (crypto markets are always open)"""
        return True  # Crypto markets are 24/7
    
    def _close_all_positions(self):
        """Close all open positions"""
        try:
            if self.strategy.position != 0:
                current_price = self.last_price
                self.strategy.close_position(current_price, datetime.now(), "bot_shutdown")
                logger.info(f"{self.name}: Closed all positions on shutdown")
        except Exception as e:
            logger.error(f"Error closing positions for {self.name}: {e}")
    
    def _save_performance_data(self):
        """Save performance data to file"""
        try:
            performance = self.strategy.calculate_performance()
            bot_stats = self.get_performance_summary()
            
            # Save to logs (in a real implementation, you might use a database)
            log_data = {
                'bot_name': self.name,
                'strategy_performance': performance,
                'bot_statistics': bot_stats,
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"{self.name} final performance: {log_data}")
            
        except Exception as e:
            logger.error(f"Error saving performance data for {self.name}: {e}")
    
    def _update_statistics(self):
        """Update bot statistics"""
        try:
            # Update from strategy
            performance = self.strategy.calculate_performance()
            
            if performance:
                self.total_trades = performance.get('total_trades', 0)
                self.successful_trades = performance.get('winning_trades', 0)
                self.total_pnl = performance.get('total_return', 0)
            
        except Exception as e:
            logger.error(f"Error updating statistics for {self.name}: {e}")
    
    def get_detailed_status(self) -> Dict[str, Any]:
        """Get detailed bot status"""
        base_status = super().get_status()
        
        # Add live trading specific status
        base_status.update({
            'current_price': self.last_price,
            'last_signal': self.last_signal,
            'strategy_position': self.strategy.position,
            'strategy_entry_price': self.strategy.entry_price,
            'trades_today': self.trades_today,
            'daily_pnl': round(self.daily_pnl, 2),
            'data_points': len(self.current_data),
            'exchange_connected': self.exchange_client.is_connected if self.exchange_client else False
        })
        
        return base_status
