# exchanges.py - Exchange Connector Base Class
import ccxt
import logging
from typing import Dict, Optional, List
from abc import ABC, abstractmethod
import os

logger = logging.getLogger(__name__)

class ExchangeConnector(ABC):
    """Base class for exchange connections"""
    
    def __init__(self, api_key: str = None, api_secret: str = None, sandbox: bool = True):
        self.api_key = api_key or os.getenv('EXCHANGE_API_KEY')
        self.api_secret = api_secret or os.getenv('EXCHANGE_API_SECRET') 
        self.sandbox = sandbox
        self.exchange = None
        self.is_connected = False
    
    @abstractmethod
    def connect(self) -> bool:
        """Connect to the exchange"""
        pass
    
    @abstractmethod
    def get_balance(self) -> Dict:
        """Get account balance"""
        pass
    
    @abstractmethod
    def place_order(self, symbol: str, side: str, amount: float, price: float = None) -> Dict:
        """Place an order"""
        pass
    
    @abstractmethod
    def get_open_orders(self, symbol: str = None) -> List[Dict]:
        """Get open orders"""
        pass
    
    @abstractmethod
    def cancel_order(self, order_id: str, symbol: str) -> bool:
        """Cancel an order"""
        pass
    
    def test_connection(self) -> bool:
        """Test exchange connection"""
        try:
            if not self.exchange:
                return False
                
            # Test with a simple balance check
            self.exchange.fetch_balance()
            self.is_connected = True
            logger.info("✅ Exchange connection test successful")
            return True
            
        except Exception as e:
            logger.error(f"❌ Exchange connection test failed: {e}")
            self.is_connected = False
            return False
    
    def get_ticker(self, symbol: str) -> Dict:
        """Get ticker information"""
        try:
            if not self.exchange:
                return {}
                
            ticker = self.exchange.fetch_ticker(symbol)
            return {
                'symbol': symbol,
                'price': ticker.get('last', 0),
                'bid': ticker.get('bid', 0),
                'ask': ticker.get('ask', 0),
                'volume': ticker.get('baseVolume', 0),
                'change_24h': ticker.get('percentage', 0)
            }
            
        except Exception as e:
            logger.error(f"❌ Error fetching ticker for {symbol}: {e}")
            return {}
    
    def get_order_book(self, symbol: str, limit: int = 20) -> Dict:
        """Get order book"""
        try:
            if not self.exchange:
                return {}
                
            orderbook = self.exchange.fetch_order_book(symbol, limit)
            return {
                'symbol': symbol,
                'bids': orderbook.get('bids', []),
                'asks': orderbook.get('asks', []),
                'timestamp': orderbook.get('timestamp')
            }
            
        except Exception as e:
            logger.error(f"❌ Error fetching order book for {symbol}: {e}")
            return {}
