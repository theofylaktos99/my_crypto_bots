# logger.py - Centralized Logging Configuration
import logging
import logging.handlers
import os
from datetime import datetime
from typing import Optional

def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    console: bool = True
) -> logging.Logger:
    """
    Setup centralized logging for the crypto trading bot
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (optional)
        max_bytes: Maximum bytes per log file
        backup_count: Number of backup files to keep
        console: Whether to log to console
        
    Returns:
        logging.Logger: Configured logger
    """
    
    # Create logs directory if it doesn't exist
    if log_file:
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Add console handler
    if console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, level.upper()))
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    # Add file handler with rotation
    if log_file:
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(getattr(logging, level.upper()))
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Reduce noise from external libraries
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('ccxt').setLevel(logging.WARNING)
    
    logger = logging.getLogger(__name__)
    logger.info("✅ Logging system initialized")
    
    return root_logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the given name"""
    return logging.getLogger(name)


class TradingLogger:
    """Specialized logger for trading operations"""
    
    def __init__(self, name: str, log_file: Optional[str] = None):
        self.logger = logging.getLogger(name)
        self.name = name
        
        if log_file:
            # Create a dedicated file handler for this logger
            handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=5 * 1024 * 1024,  # 5MB
                backupCount=3
            )
            
            formatter = logging.Formatter(
                '%(asctime)s | %(levelname)-8s | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def trade(self, action: str, symbol: str, price: float, quantity: float = None, 
              pnl: float = None, reason: str = None):
        """Log trading activity"""
        msg = f"TRADE | {action} {symbol} @ {price:.4f}"
        
        if quantity:
            msg += f" | Qty: {quantity:.4f}"
        if pnl is not None:
            msg += f" | P&L: {pnl:+.2f}%"
        if reason:
            msg += f" | Reason: {reason}"
            
        self.logger.info(msg)
    
    def signal(self, signal: str, symbol: str, indicators: dict = None):
        """Log trading signals"""
        msg = f"SIGNAL | {signal} for {symbol}"
        
        if indicators:
            indicator_str = " | ".join([f"{k}={v:.2f}" for k, v in indicators.items()])
            msg += f" | {indicator_str}"
            
        self.logger.info(msg)
    
    def error(self, message: str, error: Exception = None):
        """Log errors"""
        if error:
            self.logger.error(f"ERROR | {message}: {str(error)}")
        else:
            self.logger.error(f"ERROR | {message}")
    
    def performance(self, metrics: dict):
        """Log performance metrics"""
        msg = "PERFORMANCE |"
        for key, value in metrics.items():
            if isinstance(value, float):
                msg += f" {key}={value:.2f}"
            else:
                msg += f" {key}={value}"
        
        self.logger.info(msg)
    
    def status(self, status: str, details: dict = None):
        """Log bot status"""
        msg = f"STATUS | {status}"
        
        if details:
            detail_str = " | ".join([f"{k}={v}" for k, v in details.items()])
            msg += f" | {detail_str}"
            
        self.logger.info(msg)


# Pre-configured loggers for common use cases
def get_trading_logger(bot_name: str) -> TradingLogger:
    """Get a trading logger for a specific bot"""
    log_file = f"logs/{bot_name}_{datetime.now().strftime('%Y%m%d')}.log"
    return TradingLogger(f"trading.{bot_name}", log_file)


def get_api_logger() -> logging.Logger:
    """Get logger for API operations"""
    return logging.getLogger("api")


def get_strategy_logger() -> logging.Logger:
    """Get logger for strategy operations"""  
    return logging.getLogger("strategy")


def get_bot_logger() -> logging.Logger:
    """Get logger for bot operations"""
    return logging.getLogger("bot")


# Default logger instance for convenience
logger = logging.getLogger(__name__)
