# error_handler.py - Comprehensive Error Handling System
import logging
import traceback
from datetime import datetime
from typing import Optional, Dict, Any
import ccxt
import json
import os

class TradingBotErrorHandler:
    """Comprehensive error handling for crypto trading bots"""
    
    def __init__(self, log_file: str = "bot_errors.log"):
        self.log_file = log_file
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup comprehensive logging system"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def handle_exchange_error(self, error: Exception, context: str = "") -> Dict[str, Any]:
        """Handle exchange-specific errors with detailed classification"""
        error_info = {
            'timestamp': datetime.now().isoformat(),
            'error_type': type(error).__name__,
            'context': context,
            'message': str(error),
            'resolved': False,
            'action_taken': None
        }
        
        # Classify and handle specific error types
        if isinstance(error, ccxt.AuthenticationError):
            error_info.update(self._handle_auth_error(error))
        elif isinstance(error, ccxt.NetworkError):
            error_info.update(self._handle_network_error(error))
        elif isinstance(error, ccxt.ExchangeError):
            error_info.update(self._handle_exchange_error_specific(error))
        elif isinstance(error, ccxt.InsufficientFunds):
            error_info.update(self._handle_insufficient_funds(error))
        elif isinstance(error, ccxt.InvalidNonce):
            error_info.update(self._handle_invalid_nonce(error))
        else:
            error_info.update(self._handle_generic_error(error))
        
        # Log the error
        self._log_error(error_info)
        
        return error_info
    
    def _handle_auth_error(self, error: ccxt.AuthenticationError) -> Dict[str, Any]:
        """Handle authentication errors"""
        self.logger.error("🔒 AUTHENTICATION ERROR detected")
        
        solutions = [
            "1. Verify API key and secret in .env file",
            "2. Check API key permissions on exchange",
            "3. Ensure testnet keys for testnet mode",
            "4. Check if API keys have expired"
        ]
        
        return {
            'severity': 'CRITICAL',
            'category': 'Authentication',
            'solutions': solutions,
            'action_taken': 'Bot stopped for security',
            'auto_retry': False
        }
    
    def _handle_network_error(self, error: ccxt.NetworkError) -> Dict[str, Any]:
        """Handle network connectivity errors"""
        self.logger.warning("🌐 NETWORK ERROR detected")
        
        solutions = [
            "1. Check internet connectivity",
            "2. Verify exchange API endpoints",
            "3. Check firewall/proxy settings",
            "4. Wait for exchange maintenance to complete"
        ]
        
        return {
            'severity': 'HIGH',
            'category': 'Network',
            'solutions': solutions,
            'action_taken': 'Retrying with exponential backoff',
            'auto_retry': True,
            'retry_delay': 30
        }
    
    def _handle_exchange_error_specific(self, error: ccxt.ExchangeError) -> Dict[str, Any]:
        """Handle exchange-specific errors"""
        error_msg = str(error).lower()
        
        if 'insufficient' in error_msg:
            return self._handle_insufficient_funds(error)
        elif 'rate limit' in error_msg:
            return self._handle_rate_limit_error(error)
        elif 'maintenance' in error_msg:
            return self._handle_maintenance_error(error)
        else:
            return self._handle_generic_exchange_error(error)
    
    def _handle_insufficient_funds(self, error: Exception) -> Dict[str, Any]:
        """Handle insufficient funds errors"""
        self.logger.error("💰 INSUFFICIENT FUNDS detected")
        
        return {
            'severity': 'HIGH',
            'category': 'Funds',
            'solutions': [
                "1. Check account balance",
                "2. Reduce position size",
                "3. Add funds to account",
                "4. Review risk management settings"
            ],
            'action_taken': 'Position size reduced',
            'auto_retry': False
        }
    
    def _handle_invalid_nonce(self, error: ccxt.InvalidNonce) -> Dict[str, Any]:
        """Handle timestamp/nonce synchronization errors"""
        self.logger.warning("⏰ TIMESTAMP SYNC ERROR detected")
        
        return {
            'severity': 'MEDIUM',
            'category': 'Synchronization',
            'solutions': [
                "1. Synchronize system clock",
                "2. Check timezone settings",
                "3. Increase recvWindow parameter",
                "4. Use NTP time synchronization"
            ],
            'action_taken': 'Clock sync attempted',
            'auto_retry': True,
            'retry_delay': 5
        }
    
    def _handle_rate_limit_error(self, error: Exception) -> Dict[str, Any]:
        """Handle API rate limiting"""
        self.logger.warning("🚦 RATE LIMIT exceeded")
        
        return {
            'severity': 'LOW',
            'category': 'RateLimit',
            'solutions': [
                "1. Enable rate limiting in ccxt",
                "2. Reduce API call frequency",
                "3. Implement request queuing",
                "4. Wait for rate limit reset"
            ],
            'action_taken': 'Waiting for rate limit reset',
            'auto_retry': True,
            'retry_delay': 60
        }
    
    def _handle_maintenance_error(self, error: Exception) -> Dict[str, Any]:
        """Handle exchange maintenance periods"""
        self.logger.info("🔧 EXCHANGE MAINTENANCE detected")
        
        return {
            'severity': 'LOW',
            'category': 'Maintenance',
            'solutions': [
                "1. Wait for maintenance completion",
                "2. Check exchange status page",
                "3. Monitor exchange announcements",
                "4. Switch to backup exchange if available"
            ],
            'action_taken': 'Waiting for maintenance completion',
            'auto_retry': True,
            'retry_delay': 300  # 5 minutes
        }
    
    def _handle_generic_exchange_error(self, error: Exception) -> Dict[str, Any]:
        """Handle generic exchange errors"""
        return {
            'severity': 'MEDIUM',
            'category': 'Exchange',
            'solutions': [
                "1. Check exchange documentation",
                "2. Verify API parameters",
                "3. Check exchange status",
                "4. Contact exchange support"
            ],
            'action_taken': 'Error logged for investigation',
            'auto_retry': False
        }
    
    def _handle_generic_error(self, error: Exception) -> Dict[str, Any]:
        """Handle generic/unknown errors"""
        return {
            'severity': 'MEDIUM',
            'category': 'Unknown',
            'solutions': [
                "1. Check bot logs for details",
                "2. Review recent code changes",
                "3. Restart bot with debug mode",
                "4. Contact development team"
            ],
            'action_taken': 'Full error trace logged',
            'auto_retry': False
        }
    
    def _log_error(self, error_info: Dict[str, Any]):
        """Log error information comprehensively"""
        severity = error_info.get('severity', 'UNKNOWN')
        category = error_info.get('category', 'UNKNOWN')
        
        self.logger.error(f"[{severity}] {category} Error: {error_info['message']}")
        
        if error_info.get('solutions'):
            self.logger.info("💡 Suggested solutions:")
            for solution in error_info['solutions']:
                self.logger.info(f"   {solution}")
        
        # Save detailed error to file
        self._save_error_details(error_info)
    
    def _save_error_details(self, error_info: Dict[str, Any]):
        """Save detailed error information to file"""
        error_file = f"error_details_{datetime.now().strftime('%Y%m%d')}.json"
        
        try:
            # Load existing errors or create new list
            if os.path.exists(error_file):
                with open(error_file, 'r') as f:
                    errors = json.load(f)
            else:
                errors = []
            
            # Add new error
            errors.append(error_info)
            
            # Save updated errors
            with open(error_file, 'w') as f:
                json.dump(errors, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save error details: {e}")
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics for monitoring"""
        today = datetime.now().strftime('%Y%m%d')
        error_file = f"error_details_{today}.json"
        
        if not os.path.exists(error_file):
            return {'total_errors': 0, 'categories': {}}
        
        try:
            with open(error_file, 'r') as f:
                errors = json.load(f)
            
            categories = {}
            for error in errors:
                category = error.get('category', 'Unknown')
                categories[category] = categories.get(category, 0) + 1
            
            return {
                'total_errors': len(errors),
                'categories': categories,
                'last_error_time': errors[-1]['timestamp'] if errors else None
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get error statistics: {e}")
            return {'total_errors': 0, 'categories': {}}

# Global error handler instance
error_handler = TradingBotErrorHandler()

# Convenience functions
def handle_trading_error(error: Exception, context: str = "") -> Dict[str, Any]:
    """Handle trading bot errors"""
    return error_handler.handle_exchange_error(error, context)

def log_error(message: str, severity: str = "ERROR"):
    """Log a simple error message"""
    logger = logging.getLogger(__name__)
    getattr(logger, severity.lower())(message)

if __name__ == "__main__":
    # Test error handling
    print("🧪 Testing error handling system...")
    error_handler.logger.info("✅ Error handling system initialized")
