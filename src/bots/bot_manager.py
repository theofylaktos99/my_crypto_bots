# bot_manager.py - Centralized Bot Management System
import logging
from typing import Dict, Any, List, Optional
import threading
import time
from datetime import datetime
import uuid

from .base_bot import BaseBot
from .live_trading_bot import LiveTradingBot
from ..utils.config_manager import ConfigManager
from ..strategies import RSIEMAATRStrategy, ZScorePhiStrategy

logger = logging.getLogger(__name__)

class BotManager:
    """Centralized bot management system"""
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.active_bots: Dict[str, BaseBot] = {}
        self.bot_configs: Dict[str, Dict[str, Any]] = {}
        
        # Manager settings
        self.max_concurrent_bots = config_manager.get_config('app', 'max_concurrent_bots', 5)
        self.bot_check_interval = config_manager.get_config('bots', 'bot_check_interval', 60)
        
        # Start monitor thread
        self.monitor_thread = threading.Thread(target=self._monitor_bots, daemon=True)
        self.is_monitoring = True
        self.monitor_thread.start()
        
        logger.info("✅ Bot manager initialized")
    
    def deploy_bot(self, bot_name: str, bot_config: Dict[str, Any]) -> bool:
        """Deploy a new trading bot"""
        try:
            # Validate bot name
            if bot_name in self.active_bots:
                logger.error(f"Bot '{bot_name}' already exists")
                return False
            
            # Check concurrent bot limit
            if len(self.active_bots) >= self.max_concurrent_bots:
                logger.error(f"Maximum concurrent bots ({self.max_concurrent_bots}) reached")
                return False
            
            # Validate configuration
            if not self._validate_bot_config(bot_config):
                logger.error("Invalid bot configuration")
                return False
            
            # Create strategy instance
            strategy = self._create_strategy(bot_config.get('strategy', 'RSI_EMA_ATR'))
            if not strategy:
                logger.error(f"Failed to create strategy: {bot_config.get('strategy')}")
                return False
            
            # Create bot instance
            bot = LiveTradingBot(
                name=bot_name,
                symbol=bot_config['symbol'],
                timeframe=bot_config['timeframe'],
                strategy=strategy,
                config_manager=self.config_manager
            )
            
            # Configure bot
            bot.update_config(bot_config)
            
            # Store bot
            self.active_bots[bot_name] = bot
            self.bot_configs[bot_name] = bot_config.copy()
            
            # Save bot configuration
            self.config_manager.create_bot_config(bot_name, bot_config)
            
            logger.info(f"✅ Bot '{bot_name}' deployed successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error deploying bot '{bot_name}': {e}")
            return False
    
    def start_bot(self, bot_name: str) -> bool:
        """Start a specific bot"""
        try:
            if bot_name not in self.active_bots:
                logger.error(f"Bot '{bot_name}' not found")
                return False
            
            bot = self.active_bots[bot_name]
            success = bot.start()
            
            if success:
                logger.info(f"✅ Bot '{bot_name}' started")
            else:
                logger.error(f"❌ Failed to start bot '{bot_name}'")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Error starting bot '{bot_name}': {e}")
            return False
    
    def stop_bot(self, bot_name: str) -> bool:
        """Stop a specific bot"""
        try:
            if bot_name not in self.active_bots:
                logger.error(f"Bot '{bot_name}' not found")
                return False
            
            bot = self.active_bots[bot_name]
            bot.stop()
            
            logger.info(f"✅ Bot '{bot_name}' stopped")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error stopping bot '{bot_name}': {e}")
            return False
    
    def pause_bot(self, bot_name: str) -> bool:
        """Pause a specific bot"""
        try:
            if bot_name not in self.active_bots:
                logger.error(f"Bot '{bot_name}' not found")
                return False
            
            bot = self.active_bots[bot_name]
            bot.pause()
            
            logger.info(f"⏸️ Bot '{bot_name}' paused")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error pausing bot '{bot_name}': {e}")
            return False
    
    def resume_bot(self, bot_name: str) -> bool:
        """Resume a specific bot"""
        try:
            if bot_name not in self.active_bots:
                logger.error(f"Bot '{bot_name}' not found")
                return False
            
            bot = self.active_bots[bot_name]
            bot.resume()
            
            logger.info(f"▶️ Bot '{bot_name}' resumed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error resuming bot '{bot_name}': {e}")
            return False
    
    def remove_bot(self, bot_name: str) -> bool:
        """Remove a bot completely"""
        try:
            if bot_name not in self.active_bots:
                logger.error(f"Bot '{bot_name}' not found")
                return False
            
            # Stop bot first
            bot = self.active_bots[bot_name]
            bot.stop()
            
            # Remove from collections
            del self.active_bots[bot_name]
            if bot_name in self.bot_configs:
                del self.bot_configs[bot_name]
            
            logger.info(f"✅ Bot '{bot_name}' removed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error removing bot '{bot_name}': {e}")
            return False
    
    def get_bot_status(self, bot_name: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific bot"""
        try:
            if bot_name not in self.active_bots:
                return None
            
            bot = self.active_bots[bot_name]
            return bot.get_status()
            
        except Exception as e:
            logger.error(f"❌ Error getting bot status '{bot_name}': {e}")
            return None
    
    def get_all_bots_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all bots"""
        try:
            status_dict = {}
            
            for bot_name, bot in self.active_bots.items():
                status_dict[bot_name] = bot.get_status()
            
            return status_dict
            
        except Exception as e:
            logger.error(f"❌ Error getting all bots status: {e}")
            return {}
    
    def stop_all_bots(self) -> bool:
        """Stop all active bots"""
        try:
            success_count = 0
            
            for bot_name in list(self.active_bots.keys()):
                if self.stop_bot(bot_name):
                    success_count += 1
            
            logger.info(f"✅ Stopped {success_count}/{len(self.active_bots)} bots")
            return success_count == len(self.active_bots)
            
        except Exception as e:
            logger.error(f"❌ Error stopping all bots: {e}")
            return False
    
    def pause_all_bots(self) -> bool:
        """Pause all active bots"""
        try:
            success_count = 0
            
            for bot_name in self.active_bots.keys():
                if self.pause_bot(bot_name):
                    success_count += 1
            
            logger.info(f"⏸️ Paused {success_count}/{len(self.active_bots)} bots")
            return success_count == len(self.active_bots)
            
        except Exception as e:
            logger.error(f"❌ Error pausing all bots: {e}")
            return False
    
    def resume_all_bots(self) -> bool:
        """Resume all paused bots"""
        try:
            success_count = 0
            
            for bot_name in self.active_bots.keys():
                if self.resume_bot(bot_name):
                    success_count += 1
            
            logger.info(f"▶️ Resumed {success_count}/{len(self.active_bots)} bots")
            return success_count == len(self.active_bots)
            
        except Exception as e:
            logger.error(f"❌ Error resuming all bots: {e}")
            return False
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get overall performance summary"""
        try:
            total_bots = len(self.active_bots)
            running_bots = sum(1 for bot in self.active_bots.values() if bot.is_running)
            paused_bots = sum(1 for bot in self.active_bots.values() if bot.is_paused)
            
            total_trades = sum(bot.total_trades for bot in self.active_bots.values())
            successful_trades = sum(bot.successful_trades for bot in self.active_bots.values())
            total_pnl = sum(bot.total_pnl for bot in self.active_bots.values())
            
            success_rate = (successful_trades / total_trades * 100) if total_trades > 0 else 0
            
            return {
                'total_bots': total_bots,
                'running_bots': running_bots,
                'paused_bots': paused_bots,
                'stopped_bots': total_bots - running_bots - paused_bots,
                'total_trades': total_trades,
                'successful_trades': successful_trades,
                'success_rate': round(success_rate, 2),
                'total_pnl': round(total_pnl, 2),
                'average_pnl_per_bot': round(total_pnl / total_bots, 2) if total_bots > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting performance summary: {e}")
            return {}
    
    def _validate_bot_config(self, config: Dict[str, Any]) -> bool:
        """Validate bot configuration"""
        required_fields = ['symbol', 'timeframe', 'strategy']
        
        for field in required_fields:
            if field not in config:
                logger.error(f"Missing required field: {field}")
                return False
        
        # Validate symbol format
        if '/' not in config['symbol']:
            logger.error("Invalid symbol format. Use format like 'BTC/USDT'")
            return False
        
        # Validate timeframe
        valid_timeframes = ['1m', '5m', '15m', '30m', '1h', '4h', '1d']
        if config['timeframe'] not in valid_timeframes:
            logger.error(f"Invalid timeframe. Must be one of: {valid_timeframes}")
            return False
        
        # Validate strategy
        valid_strategies = ['RSI_EMA_ATR', 'ZSCORE_PHI']
        if config['strategy'] not in valid_strategies:
            logger.error(f"Invalid strategy. Must be one of: {valid_strategies}")
            return False
        
        return True
    
    def _create_strategy(self, strategy_name: str):
        """Create strategy instance"""
        try:
            strategy_config = self.config_manager.get_strategy_config(strategy_name)
            parameters = strategy_config.get('parameters', {})
            
            if strategy_name == 'RSI_EMA_ATR':
                return RSIEMAATRStrategy(**parameters)
            elif strategy_name == 'ZSCORE_PHI':
                return ZScorePhiStrategy(**parameters)
            else:
                logger.error(f"Unknown strategy: {strategy_name}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating strategy '{strategy_name}': {e}")
            return None
    
    def _monitor_bots(self):
        """Monitor bot health and performance"""
        logger.info("Started bot monitoring thread")
        
        while self.is_monitoring:
            try:
                # Check each bot's health
                for bot_name, bot in list(self.active_bots.items()):
                    self._check_bot_health(bot_name, bot)
                
                # Sleep until next check
                time.sleep(self.bot_check_interval)
                
            except Exception as e:
                logger.error(f"Error in bot monitoring: {e}")
                time.sleep(60)  # Wait longer on error
        
        logger.info("Bot monitoring thread stopped")
    
    def _check_bot_health(self, bot_name: str, bot: BaseBot):
        """Check individual bot health"""
        try:
            # Check if bot thread is alive
            if bot.is_running and (not bot.thread or not bot.thread.is_alive()):
                logger.warning(f"Bot '{bot_name}' thread died, attempting restart...")
                bot.start()
            
            # Check for errors
            if bot.last_error:
                logger.warning(f"Bot '{bot_name}' has error: {bot.last_error}")
            
            # Log bot status periodically
            if hasattr(self, '_last_health_check'):
                time_since_last = time.time() - self._last_health_check
                if time_since_last > 3600:  # Log every hour
                    status = bot.get_status()
                    logger.info(f"Bot '{bot_name}' health: {status}")
            
            self._last_health_check = time.time()
            
        except Exception as e:
            logger.error(f"Error checking health of bot '{bot_name}': {e}")
    
    def shutdown(self):
        """Shutdown the bot manager"""
        try:
            logger.info("Shutting down bot manager...")
            
            # Stop monitoring
            self.is_monitoring = False
            
            # Stop all bots
            self.stop_all_bots()
            
            # Wait for monitor thread
            if self.monitor_thread.is_alive():
                self.monitor_thread.join(timeout=5)
            
            logger.info("✅ Bot manager shutdown complete")
            
        except Exception as e:
            logger.error(f"❌ Error during bot manager shutdown: {e}")
    
    def __del__(self):
        """Cleanup on deletion"""
        try:
            self.shutdown()
        except:
            pass  # Ignore errors during cleanup
