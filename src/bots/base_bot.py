# base_bot.py - Base Trading Bot Class
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging
import threading
import time
from datetime import datetime
import pandas as pd

logger = logging.getLogger(__name__)

class BaseBot(ABC):
    """Base class for all trading bots"""
    
    def __init__(self, name: str, symbol: str, timeframe: str):
        self.name = name
        self.symbol = symbol
        self.timeframe = timeframe
        self.is_running = False
        self.is_paused = False
        self.thread = None
        
        # Bot statistics
        self.start_time = None
        self.total_trades = 0
        self.successful_trades = 0
        self.total_pnl = 0.0
        self.last_signal_time = None
        self.last_error = None
        
        # Configuration
        self.config = {}
        self.risk_config = {
            'max_position_size': 0.1,  # 10% of balance
            'risk_per_trade': 0.02,     # 2% risk per trade
            'max_daily_trades': 10,
            'max_daily_loss': 0.05     # 5% max daily loss
        }
        
        logger.info(f"Initialized bot: {self.name} for {self.symbol} on {self.timeframe}")
    
    @abstractmethod
    def initialize(self) -> bool:
        """Initialize bot components (exchange, strategy, etc.)"""
        pass
    
    @abstractmethod
    def run_cycle(self) -> bool:
        """Execute one trading cycle"""
        pass
    
    @abstractmethod
    def cleanup(self):
        """Cleanup resources when stopping"""
        pass
    
    def start(self) -> bool:
        """Start the trading bot"""
        try:
            if self.is_running:
                logger.warning(f"Bot {self.name} is already running")
                return False
            
            # Initialize bot components
            if not self.initialize():
                logger.error(f"Failed to initialize bot {self.name}")
                return False
            
            self.is_running = True
            self.is_paused = False
            self.start_time = datetime.now()
            
            # Start bot thread
            self.thread = threading.Thread(target=self._bot_loop, daemon=True)
            self.thread.start()
            
            logger.info(f"✅ Started bot: {self.name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error starting bot {self.name}: {e}")
            self.is_running = False
            return False
    
    def stop(self):
        """Stop the trading bot"""
        try:
            logger.info(f"Stopping bot: {self.name}")
            self.is_running = False
            
            # Wait for thread to finish
            if self.thread and self.thread.is_alive():
                self.thread.join(timeout=5)
            
            # Cleanup resources
            self.cleanup()
            
            logger.info(f"✅ Stopped bot: {self.name}")
            
        except Exception as e:
            logger.error(f"❌ Error stopping bot {self.name}: {e}")
    
    def pause(self):
        """Pause the trading bot"""
        if self.is_running:
            self.is_paused = True
            logger.info(f"⏸️ Paused bot: {self.name}")
    
    def resume(self):
        """Resume the trading bot"""
        if self.is_running and self.is_paused:
            self.is_paused = False
            logger.info(f"▶️ Resumed bot: {self.name}")
    
    def _bot_loop(self):
        """Main bot execution loop"""
        logger.info(f"Starting trading loop for {self.name}")
        
        while self.is_running:
            try:
                if not self.is_paused:
                    # Execute one trading cycle
                    success = self.run_cycle()
                    
                    if not success:
                        logger.warning(f"Trading cycle failed for {self.name}")
                        
                    # Update last signal time
                    self.last_signal_time = datetime.now()
                
                # Sleep between cycles
                time.sleep(self._get_sleep_duration())
                
            except KeyboardInterrupt:
                logger.info(f"Keyboard interrupt received for {self.name}")
                break
            except Exception as e:
                logger.error(f"Error in bot loop for {self.name}: {e}")
                self.last_error = str(e)
                time.sleep(60)  # Wait longer on error
        
        logger.info(f"Trading loop ended for {self.name}")
    
    def _get_sleep_duration(self) -> int:
        """Get sleep duration based on timeframe"""
        timeframe_sleep = {
            '1m': 60,      # 1 minute
            '5m': 300,     # 5 minutes
            '15m': 900,    # 15 minutes
            '30m': 1800,   # 30 minutes
            '1h': 3600,    # 1 hour
            '4h': 14400,   # 4 hours
            '1d': 86400    # 1 day
        }
        
        return timeframe_sleep.get(self.timeframe, 300)  # Default 5 minutes
    
    def get_status(self) -> Dict[str, Any]:
        """Get current bot status"""
        uptime = None
        if self.start_time:
            uptime = str(datetime.now() - self.start_time)
        
        return {
            'name': self.name,
            'symbol': self.symbol,
            'timeframe': self.timeframe,
            'is_running': self.is_running,
            'is_paused': self.is_paused,
            'uptime': uptime,
            'total_trades': self.total_trades,
            'successful_trades': self.successful_trades,
            'success_rate': (self.successful_trades / self.total_trades * 100) if self.total_trades > 0 else 0,
            'total_pnl': self.total_pnl,
            'last_signal_time': self.last_signal_time,
            'last_error': self.last_error,
            'thread_alive': self.thread.is_alive() if self.thread else False
        }
    
    def update_config(self, config: Dict[str, Any]):
        """Update bot configuration"""
        self.config.update(config)
        logger.info(f"Updated config for {self.name}")
    
    def update_risk_config(self, risk_config: Dict[str, Any]):
        """Update risk management configuration"""
        self.risk_config.update(risk_config)
        logger.info(f"Updated risk config for {self.name}")
    
    def log_trade(self, action: str, price: float, quantity: float = None, 
                  pnl: float = None, reason: str = None):
        """Log trading activity"""
        self.total_trades += 1
        
        if pnl and pnl > 0:
            self.successful_trades += 1
            
        if pnl:
            self.total_pnl += pnl
        
        log_msg = f"[{self.name}] {action} {self.symbol} @ {price:.4f}"
        if quantity:
            log_msg += f" | Qty: {quantity:.4f}"
        if pnl:
            log_msg += f" | P&L: {pnl:.2f}%"
        if reason:
            log_msg += f" | Reason: {reason}"
            
        logger.info(log_msg)
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get bot performance summary"""
        return {
            'bot_name': self.name,
            'symbol': self.symbol,
            'timeframe': self.timeframe,
            'total_trades': self.total_trades,
            'successful_trades': self.successful_trades,
            'success_rate': (self.successful_trades / self.total_trades * 100) if self.total_trades > 0 else 0,
            'total_pnl': round(self.total_pnl, 2),
            'average_pnl': round(self.total_pnl / self.total_trades, 2) if self.total_trades > 0 else 0,
            'uptime': str(datetime.now() - self.start_time) if self.start_time else None,
            'risk_per_trade': self.risk_config.get('risk_per_trade', 0),
            'max_position_size': self.risk_config.get('max_position_size', 0)
        }
