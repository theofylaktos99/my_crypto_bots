# Bots Module - Trading Bot Implementations  
__version__ = "1.0.0"

from .base_bot import BaseBot
from .live_trading_bot import LiveTradingBot
from .backtesting_bot import BacktestingBot
from .bot_manager import BotManager

__all__ = [
    'BaseBot',
    'LiveTradingBot', 
    'BacktestingBot',
    'BotManager'
]
