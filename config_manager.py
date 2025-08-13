# config_manager.py - Secure Configuration Management
import os
from dotenv import load_dotenv
import logging
from typing import Optional
import json

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecurityConfig:
    """Secure configuration management for crypto trading bots"""
    
    def __init__(self, env_file: str = ".env"):
        self.env_file = env_file
        self._load_environment()
        self._validate_config()
    
    def _load_environment(self):
        """Load environment variables securely"""
        try:
            load_dotenv(self.env_file)
            logger.info("✅ Environment variables loaded successfully")
        except Exception as e:
            logger.error(f"❌ Failed to load .env file: {e}")
            raise
    
    def _validate_config(self):
        """Validate critical configuration parameters"""
        required_vars = ['API_KEY', 'SECRET_KEY']
        missing_vars = []
        
        for var in required_vars:
            if not self.get_api_credential(var):
                missing_vars.append(var)
        
        if missing_vars:
            logger.warning(f"⚠️ Missing required variables: {missing_vars}")
        
        # Validate testnet setting
        if not self.is_testnet():
            logger.warning("⚠️ WARNING: MAINNET mode detected. Use with extreme caution!")
    
    def get_api_credential(self, key: str) -> Optional[str]:
        """Safely get API credentials"""
        value = os.getenv(key)
        if not value or value.startswith('your_'):
            logger.warning(f"⚠️ {key} not properly configured")
            return None
        return value
    
    def is_testnet(self) -> bool:
        """Check if testnet mode is enabled"""
        return os.getenv('USE_TESTNET', 'True').lower() == 'true'
    
    def get_risk_settings(self) -> dict:
        """Get risk management settings"""
        return {
            'max_position_size': float(os.getenv('MAX_POSITION_SIZE', '0.01')),
            'risk_per_trade': float(os.getenv('RISK_PER_TRADE', '0.02')),
            'max_daily_trades': int(os.getenv('MAX_DAILY_TRADES', '10')),
            'max_drawdown': float(os.getenv('MAX_DRAWDOWN', '0.05'))
        }
    
    def get_exchange_config(self) -> dict:
        """Get exchange configuration"""
        config = {
            'apiKey': self.get_api_credential('API_KEY'),
            'secret': self.get_api_credential('SECRET_KEY'),
            'enableRateLimit': True,
            'sandbox': self.is_testnet(),
            'timeout': int(os.getenv('API_TIMEOUT', '30000')),
            'rateLimit': int(os.getenv('RATE_LIMIT', '1200'))
        }
        
        # Remove None values
        return {k: v for k, v in config.items() if v is not None}
    
    def validate_api_keys(self) -> bool:
        """Validate that API keys are properly configured"""
        api_key = self.get_api_credential('API_KEY')
        secret_key = self.get_api_credential('SECRET_KEY')
        
        if not api_key or not secret_key:
            logger.error("❌ API credentials not configured")
            return False
        
        if api_key.startswith('your_') or secret_key.startswith('your_'):
            logger.error("❌ Please replace dummy API keys with real ones")
            return False
        
        logger.info("✅ API credentials appear to be configured")
        return True
    
    def log_security_status(self):
        """Log current security configuration status"""
        logger.info("🔒 Security Configuration Status:")
        logger.info(f"   Testnet Mode: {'✅ Enabled' if self.is_testnet() else '❌ DISABLED (MAINNET)'}")
        logger.info(f"   API Keys: {'✅ Configured' if self.validate_api_keys() else '❌ Not Configured'}")
        
        risk_settings = self.get_risk_settings()
        logger.info("🛡️ Risk Management Settings:")
        for key, value in risk_settings.items():
            logger.info(f"   {key}: {value}")

# Global instance
security_config = SecurityConfig()

# Convenience functions
def get_exchange_config():
    """Get secure exchange configuration"""
    return security_config.get_exchange_config()

def is_development_mode():
    """Check if we're in development/testnet mode"""
    return security_config.is_testnet()

def validate_security():
    """Validate security configuration"""
    return security_config.validate_api_keys()

if __name__ == "__main__":
    # Test the configuration
    security_config.log_security_status()
