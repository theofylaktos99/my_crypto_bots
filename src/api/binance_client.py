# binance_client.py - Binance Exchange Implementation
import ccxt
import logging
from typing import Dict, List, Optional
from .exchanges import ExchangeConnector

logger = logging.getLogger(__name__)

class BinanceClient(ExchangeConnector):
    """Binance exchange implementation"""
    
    def __init__(self, api_key: str = None, api_secret: str = None, sandbox: bool = True):
        super().__init__(api_key, api_secret, sandbox)
        self.exchange_name = "Binance"
    
    def connect(self) -> bool:
        """Connect to Binance exchange"""
        try:
            self.exchange = ccxt.binance({
                'apiKey': self.api_key,
                'secret': self.api_secret,
                'sandbox': self.sandbox,
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'spot'  # Use spot trading
                }
            })
            
            # Test the connection
            if self.test_connection():
                logger.info("✅ Successfully connected to Binance")
                return True
            else:
                logger.error("❌ Failed to connect to Binance")
                return False
                
        except Exception as e:
            logger.error(f"❌ Binance connection error: {e}")
            return False
    
    def get_balance(self) -> Dict:
        """Get Binance account balance"""
        try:
            if not self.exchange:
                return {}
            
            balance = self.exchange.fetch_balance()
            
            # Format the balance data
            formatted_balance = {}
            for currency, amounts in balance.items():
                if isinstance(amounts, dict) and amounts.get('total', 0) > 0:
                    formatted_balance[currency] = {
                        'free': amounts.get('free', 0),
                        'used': amounts.get('used', 0), 
                        'total': amounts.get('total', 0)
                    }
            
            logger.info(f"✅ Retrieved balance for {len(formatted_balance)} currencies")
            return formatted_balance
            
        except Exception as e:
            logger.error(f"❌ Error fetching Binance balance: {e}")
            return {}
    
    def place_order(self, symbol: str, side: str, amount: float, price: float = None) -> Dict:
        """Place order on Binance"""
        try:
            if not self.exchange:
                return {}
            
            order_type = 'market' if price is None else 'limit'
            
            order = self.exchange.create_order(
                symbol=symbol,
                type=order_type,
                side=side.lower(),
                amount=amount,
                price=price
            )
            
            logger.info(f"✅ {side.upper()} order placed: {order.get('id')}")
            return order
            
        except Exception as e:
            logger.error(f"❌ Error placing {side} order for {symbol}: {e}")
            return {}
    
    def get_open_orders(self, symbol: str = None) -> List[Dict]:
        """Get open orders from Binance"""
        try:
            if not self.exchange:
                return []
            
            orders = self.exchange.fetch_open_orders(symbol)
            
            formatted_orders = []
            for order in orders:
                formatted_orders.append({
                    'id': order.get('id'),
                    'symbol': order.get('symbol'),
                    'side': order.get('side'),
                    'type': order.get('type'),
                    'amount': order.get('amount'),
                    'price': order.get('price'),
                    'status': order.get('status'),
                    'timestamp': order.get('timestamp')
                })
            
            logger.info(f"✅ Retrieved {len(formatted_orders)} open orders")
            return formatted_orders
            
        except Exception as e:
            logger.error(f"❌ Error fetching open orders: {e}")
            return []
    
    def cancel_order(self, order_id: str, symbol: str) -> bool:
        """Cancel order on Binance"""
        try:
            if not self.exchange:
                return False
            
            result = self.exchange.cancel_order(order_id, symbol)
            
            if result.get('status') == 'canceled':
                logger.info(f"✅ Order {order_id} canceled successfully")
                return True
            else:
                logger.warning(f"⚠️ Order {order_id} cancellation status: {result.get('status')}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error canceling order {order_id}: {e}")
            return False
    
    def get_trading_fees(self, symbol: str = None) -> Dict:
        """Get trading fees"""
        try:
            if not self.exchange:
                return {}
            
            fees = self.exchange.fetch_trading_fees()
            
            if symbol and symbol in fees:
                return {
                    'maker': fees[symbol].get('maker', 0),
                    'taker': fees[symbol].get('taker', 0)
                }
            
            return fees
            
        except Exception as e:
            logger.error(f"❌ Error fetching trading fees: {e}")
            return {}
    
    def get_account_info(self) -> Dict:
        """Get comprehensive account information"""
        try:
            if not self.exchange:
                return {}
            
            # Get balance
            balance = self.get_balance()
            
            # Get trading fees
            fees = self.get_trading_fees()
            
            # Get open orders count
            open_orders = len(self.get_open_orders())
            
            return {
                'exchange': self.exchange_name,
                'balance': balance,
                'fees': fees,
                'open_orders_count': open_orders,
                'is_connected': self.is_connected,
                'sandbox_mode': self.sandbox
            }
            
        except Exception as e:
            logger.error(f"❌ Error fetching account info: {e}")
            return {}
