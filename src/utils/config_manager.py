# config_manager.py - Centralized Configuration Management
import os
import json
import yaml
from typing import Dict, Any, Optional
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class ConfigManager:
    """Centralized configuration management for crypto trading bots"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        
        # Default configurations
        self.configs = {
            'app': {},
            'exchange': {},
            'strategies': {},
            'bots': {},
            'risk': {}
        }
        
        # Load configurations
        self._load_all_configs()
        
        logger.info("✅ Configuration manager initialized")
    
    def _load_all_configs(self):
        """Load all configuration files"""
        config_files = {
            'app': 'app_config.yaml',
            'exchange': 'exchange_config.yaml', 
            'strategies': 'strategies_config.yaml',
            'bots': 'bots_config.yaml',
            'risk': 'risk_config.yaml'
        }
        
        for config_type, filename in config_files.items():
            config_path = self.config_dir / filename
            
            if config_path.exists():
                self.configs[config_type] = self._load_config_file(config_path)
            else:
                # Create default config
                self.configs[config_type] = self._get_default_config(config_type)
                self._save_config_file(config_path, self.configs[config_type])
    
    def _load_config_file(self, config_path: Path) -> Dict[str, Any]:
        """Load configuration from file"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                if config_path.suffix.lower() in ['.yaml', '.yml']:
                    return yaml.safe_load(f) or {}
                elif config_path.suffix.lower() == '.json':
                    return json.load(f)
                else:
                    logger.error(f"Unsupported config file format: {config_path}")
                    return {}
                    
        except Exception as e:
            logger.error(f"Error loading config file {config_path}: {e}")
            return {}
    
    def _save_config_file(self, config_path: Path, config: Dict[str, Any]):
        """Save configuration to file"""
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                if config_path.suffix.lower() in ['.yaml', '.yml']:
                    yaml.dump(config, f, default_flow_style=False, indent=2)
                elif config_path.suffix.lower() == '.json':
                    json.dump(config, f, indent=2)
                    
            logger.info(f"✅ Saved config to {config_path}")
            
        except Exception as e:
            logger.error(f"Error saving config file {config_path}: {e}")
    
    def _get_default_config(self, config_type: str) -> Dict[str, Any]:
        """Get default configuration for a given type"""
        defaults = {
            'app': {
                'name': 'Crypto Trading Bot System',
                'version': '1.0.0',
                'environment': 'development',
                'debug': True,
                'timezone': 'UTC',
                'data_retention_days': 30,
                'max_concurrent_bots': 5
            },
            
            'exchange': {
                'default_exchange': 'binance',
                'sandbox_mode': True,
                'api_timeout': 30,
                'rate_limit': True,
                'exchanges': {
                    'binance': {
                        'name': 'Binance',
                        'sandbox_url': 'https://testnet.binance.vision',
                        'api_url': 'https://api.binance.com',
                        'enabled': True
                    }
                }
            },
            
            'strategies': {
                'default_strategy': 'RSI_EMA_ATR',
                'strategies': {
                    'RSI_EMA_ATR': {
                        'name': 'RSI + EMA + ATR Strategy',
                        'enabled': True,
                        'parameters': {
                            'rsi_period': 14,
                            'ema_period': 200,
                            'atr_period': 14,
                            'oversold_threshold': 30,
                            'overbought_threshold': 70,
                            'atr_stop_multiplier': 1.5,
                            'atr_profit_multiplier': 2.0
                        }
                    },
                    'ZSCORE_PHI': {
                        'name': 'Z-Score Phi Strategy',
                        'enabled': True,
                        'parameters': {
                            'lookback': 21,
                            'entry_threshold': 1.618,
                            'exit_threshold': 0.5
                        }
                    }
                }
            },
            
            'bots': {
                'default_timeframe': '1h',
                'max_bots_per_symbol': 1,
                'bot_check_interval': 60,
                'auto_restart': True,
                'performance_tracking': True
            },
            
            'risk': {
                'max_position_size': 0.1,     # 10% of balance
                'risk_per_trade': 0.02,       # 2% risk per trade
                'max_daily_trades': 10,
                'max_daily_loss': 0.05,       # 5% max daily loss
                'max_concurrent_positions': 3,
                'stop_loss_required': True,
                'take_profit_required': False,
                'emergency_stop_loss': 0.1    # 10% emergency stop
            }
        }
        
        return defaults.get(config_type, {})
    
    def get_config(self, config_type: str, key: str = None, default: Any = None) -> Any:
        """Get configuration value"""
        try:
            config = self.configs.get(config_type, {})
            
            if key is None:
                return config
            
            # Support nested keys like 'strategies.RSI_EMA_ATR.parameters.rsi_period'
            keys = key.split('.')
            value = config
            
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default
            
            return value
            
        except Exception as e:
            logger.error(f"Error getting config {config_type}.{key}: {e}")
            return default
    
    def set_config(self, config_type: str, key: str, value: Any) -> bool:
        """Set configuration value"""
        try:
            if config_type not in self.configs:
                self.configs[config_type] = {}
            
            # Support nested keys
            keys = key.split('.')
            config = self.configs[config_type]
            
            # Navigate to the parent of the target key
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                config = config[k]
            
            # Set the value
            config[keys[-1]] = value
            
            # Save to file
            config_files = {
                'app': 'app_config.yaml',
                'exchange': 'exchange_config.yaml',
                'strategies': 'strategies_config.yaml', 
                'bots': 'bots_config.yaml',
                'risk': 'risk_config.yaml'
            }
            
            if config_type in config_files:
                config_path = self.config_dir / config_files[config_type]
                self._save_config_file(config_path, self.configs[config_type])
            
            logger.info(f"✅ Updated config {config_type}.{key} = {value}")
            return True
            
        except Exception as e:
            logger.error(f"Error setting config {config_type}.{key}: {e}")
            return False
    
    def get_exchange_config(self, exchange_name: str = None) -> Dict[str, Any]:
        """Get exchange configuration"""
        if not exchange_name:
            exchange_name = self.get_config('exchange', 'default_exchange', 'binance')
        
        exchange_config = self.get_config('exchange', f'exchanges.{exchange_name}', {})
        
        # Add API credentials from environment
        exchange_config.update({
            'api_key': os.getenv(f'{exchange_name.upper()}_API_KEY'),
            'api_secret': os.getenv(f'{exchange_name.upper()}_API_SECRET'),
            'sandbox_mode': self.get_config('exchange', 'sandbox_mode', True)
        })
        
        return exchange_config
    
    def get_strategy_config(self, strategy_name: str) -> Dict[str, Any]:
        """Get strategy configuration"""
        return self.get_config('strategies', f'strategies.{strategy_name}', {})
    
    def get_risk_config(self) -> Dict[str, Any]:
        """Get risk management configuration"""
        return self.get_config('risk')
    
    def get_bot_config(self) -> Dict[str, Any]:
        """Get bot configuration"""
        return self.get_config('bots')
    
    def create_bot_config(self, bot_name: str, config: Dict[str, Any]) -> bool:
        """Create configuration for a specific bot"""
        try:
            bot_config_path = self.config_dir / f"bot_{bot_name}.yaml"
            self._save_config_file(bot_config_path, config)
            return True
        except Exception as e:
            logger.error(f"Error creating bot config for {bot_name}: {e}")
            return False
    
    def load_bot_config(self, bot_name: str) -> Dict[str, Any]:
        """Load configuration for a specific bot"""
        try:
            bot_config_path = self.config_dir / f"bot_{bot_name}.yaml"
            if bot_config_path.exists():
                return self._load_config_file(bot_config_path)
            return {}
        except Exception as e:
            logger.error(f"Error loading bot config for {bot_name}: {e}")
            return {}
    
    def validate_config(self) -> bool:
        """Validate all configurations"""
        try:
            # Check required API credentials
            exchange_name = self.get_config('exchange', 'default_exchange')
            exchange_config = self.get_exchange_config(exchange_name)
            
            if not exchange_config.get('api_key') or not exchange_config.get('api_secret'):
                logger.warning(f"Missing API credentials for {exchange_name}")
                return False
            
            # Check strategy configurations
            strategies = self.get_config('strategies', 'strategies', {})
            if not strategies:
                logger.error("No strategies configured")
                return False
            
            # Check risk parameters
            risk_config = self.get_risk_config()
            if risk_config.get('max_position_size', 0) <= 0:
                logger.error("Invalid max_position_size in risk config")
                return False
            
            logger.info("✅ Configuration validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            return False
    
    def get_all_configs(self) -> Dict[str, Dict[str, Any]]:
        """Get all configurations"""
        return self.configs.copy()
    
    def reset_config(self, config_type: str) -> bool:
        """Reset configuration to defaults"""
        try:
            self.configs[config_type] = self._get_default_config(config_type)
            
            config_files = {
                'app': 'app_config.yaml',
                'exchange': 'exchange_config.yaml',
                'strategies': 'strategies_config.yaml',
                'bots': 'bots_config.yaml', 
                'risk': 'risk_config.yaml'
            }
            
            if config_type in config_files:
                config_path = self.config_dir / config_files[config_type]
                self._save_config_file(config_path, self.configs[config_type])
            
            logger.info(f"✅ Reset {config_type} configuration to defaults")
            return True
            
        except Exception as e:
            logger.error(f"Error resetting {config_type} config: {e}")
            return False
