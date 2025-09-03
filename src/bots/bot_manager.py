# Trading Bot Manager - Backend Module
import os
import json
import yaml
import subprocess
import threading
import time
from datetime import datetime
import pandas as pd

class TradingBotManager:
    def __init__(self):
        self.active_bots = {}
        self.bot_configs_dir = "bot_configs"
        self.logs_dir = "bot_logs"
        os.makedirs(self.bot_configs_dir, exist_ok=True)
        os.makedirs(self.logs_dir, exist_ok=True)
    
    def deploy_bot(self, bot_name, strategy, config):
        """Deploy a new trading bot"""
        try:
            # Save configuration
            config_file = os.path.join(self.bot_configs_dir, f"{bot_name}.yaml")
            with open(config_file, 'w') as f:
                yaml.dump(config, f)
            
            # Start bot process (simulate)
            bot_info = {
                'name': bot_name,
                'strategy': strategy,
                'status': 'running',
                'started_at': datetime.now(),
                'config_file': config_file,
                'process_id': f"bot_{len(self.active_bots) + 1}",
                'stats': {
                    'total_trades': 0,
                    'profitable_trades': 0,
                    'total_pnl': 0.0,
                    'last_trade': None
                }
            }
            
            self.active_bots[bot_name] = bot_info
            
            # Log deployment
            self.log_bot_event(bot_name, "DEPLOYED", f"Bot deployed with strategy: {strategy}")
            
            return True, "Bot deployed successfully"
            
        except Exception as e:
            return False, str(e)
    
    def stop_bot(self, bot_name):
        """Stop a running bot"""
        if bot_name in self.active_bots:
            self.active_bots[bot_name]['status'] = 'stopped'
            self.log_bot_event(bot_name, "STOPPED", "Bot stopped by user")
            return True, "Bot stopped successfully"
        return False, "Bot not found"
    
    def pause_bot(self, bot_name):
        """Pause a running bot"""
        if bot_name in self.active_bots:
            self.active_bots[bot_name]['status'] = 'paused'
            self.log_bot_event(bot_name, "PAUSED", "Bot paused by user")
            return True, "Bot paused successfully"
        return False, "Bot not found"
    
    def resume_bot(self, bot_name):
        """Resume a paused bot"""
        if bot_name in self.active_bots:
            self.active_bots[bot_name]['status'] = 'running'
            self.log_bot_event(bot_name, "RESUMED", "Bot resumed by user")
            return True, "Bot resumed successfully"
        return False, "Bot not found"
    
    def get_bot_status(self, bot_name):
        """Get current status of a bot"""
        if bot_name in self.active_bots:
            return self.active_bots[bot_name]
        return None
    
    def get_all_bots(self):
        """Get all active bots"""
        return self.active_bots
    
    def log_bot_event(self, bot_name, event_type, message):
        """Log bot events"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'bot_name': bot_name,
            'event_type': event_type,
            'message': message
        }
        
        log_file = os.path.join(self.logs_dir, f"{bot_name}.json")
        
        # Load existing logs
        logs = []
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                logs = json.load(f)
        
        # Add new log entry
        logs.append(log_entry)
        
        # Keep only last 1000 entries
        logs = logs[-1000:]
        
        # Save logs
        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)
    
    def get_bot_logs(self, bot_name, limit=50):
        """Get bot logs"""
        log_file = os.path.join(self.logs_dir, f"{bot_name}.json")
        
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                logs = json.load(f)
            return logs[-limit:] if logs else []
        return []
    
    def simulate_trading(self, bot_name):
        """Simulate trading activity for demonstration"""
        if bot_name not in self.active_bots:
            return
            
        bot = self.active_bots[bot_name]
        
        if bot['status'] != 'running':
            return
        
        import random
        
        # Simulate a trade
        if random.random() < 0.1:  # 10% chance of trade per update
            trade_type = random.choice(['BUY', 'SELL'])
            pair = random.choice(['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'ADA/USDT'])
            amount = round(random.uniform(0.001, 1.0), 6)
            price = random.uniform(1000, 70000)
            pnl = random.uniform(-50, 100)
            
            # Update bot stats
            bot['stats']['total_trades'] += 1
            if pnl > 0:
                bot['stats']['profitable_trades'] += 1
            bot['stats']['total_pnl'] += pnl
            bot['stats']['last_trade'] = datetime.now()
            
            # Log the trade
            self.log_bot_event(
                bot_name,
                "TRADE",
                f"{trade_type} {amount} {pair} @ ${price:.2f} | P&L: ${pnl:.2f}"
            )

# Global bot manager instance
bot_manager = TradingBotManager()
