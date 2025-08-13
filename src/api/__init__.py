# API Module - Market Data and Exchange Integration
__version__ = "1.0.0"

from .market_data import MarketDataFetcher
from .exchanges import ExchangeConnector
from .binance_client import BinanceClient

__all__ = [
    'MarketDataFetcher',
    'ExchangeConnector', 
    'BinanceClient'
]
