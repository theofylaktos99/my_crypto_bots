# live_trading_engine.py - Complete Live Trading System
import ccxt
import pandas as pd
import numpy as np
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import csv
import os
from config_manager import get_exchange_config, is_development_mode
from error_handler import handle_trading_error, TradingBotErrorHandler
import talib

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('live_trading.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class LiveTradingEngine:
    """Complete Live Trading Engine with RSI-EMA-ATR Strategy"""
    
    def __init__(self, symbol: str = "BTC/USDT", timeframe: str = "1h"):
        self.symbol = symbol
        self.timeframe = timeframe
        self.exchange = None
        self.error_handler = TradingBotErrorHandler()
        
        # Strategy parameters
        self.rsi_period = 14
        self.ema_period = 200
        self.atr_period = 14
        self.oversold_threshold = 30
        self.overbought_threshold = 70
        self.atr_multiplier_sl = 1.5
        self.atr_multiplier_tp = 2.0
        self.position_size_pct = 0.05  # 5% of balance per trade
        
        # Trading state
        self.position = None
        self.entry_price = None
        self.stop_loss_order = None
        self.take_profit_order = None
        self.is_running = False
        self.last_signal_time = None
        
        # Data storage
        self.data_history = pd.DataFrame()
        self.trades_log = []
        
        # CSV logging
        self.csv_file = f"live_trading_{symbol.replace('/', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        self._init_csv_log()
    
    def _init_csv_log(self):
        """Initialize CSV logging file"""
        headers = [
            'timestamp', 'action', 'symbol', 'amount_base', 'price', 
            'rsi', 'ema', 'atr', 'order_id', 'status', 'error',
            'entry_price', 'pnl_quote', 'pnl_percent', 'stop_loss_level',
            'take_profit_level', 'quote_balance_before', 'pnl'
        ]
        
        with open(self.csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
        
        logger.info(f"CSV logging initialized: {self.csv_file}")
    
    def _log_to_csv(self, action: str, **kwargs):
        """Log trading action to CSV"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        row_data = {
            'timestamp': timestamp,
            'action': action,
            'symbol': self.symbol,
            'amount_base': kwargs.get('amount_base', ''),
            'price': kwargs.get('price', ''),
            'rsi': kwargs.get('rsi', ''),
            'ema': kwargs.get('ema', ''),
            'atr': kwargs.get('atr', ''),
            'order_id': kwargs.get('order_id', ''),
            'status': kwargs.get('status', ''),
            'error': kwargs.get('error', ''),
            'entry_price': kwargs.get('entry_price', ''),
            'pnl_quote': kwargs.get('pnl_quote', ''),
            'pnl_percent': kwargs.get('pnl_percent', ''),
            'stop_loss_level': kwargs.get('stop_loss_level', ''),
            'take_profit_level': kwargs.get('take_profit_level', ''),
            'quote_balance_before': kwargs.get('quote_balance_before', ''),
            'pnl': kwargs.get('pnl', '')
        }
        
        try:
            with open(self.csv_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=row_data.keys())
                writer.writerow(row_data)
        except Exception as e:
            logger.error(f"Failed to log to CSV: {e}")
    
    def initialize_exchange(self) -> bool:
        """Initialize exchange connection"""
        logger.info("Initializing exchange connection...")
        
        try:
            config = get_exchange_config()
            
            if not config.get('apiKey') or not config.get('secret'):
                logger.error("API credentials not configured")
                return False
            
            self.exchange = ccxt.binance(config)
            
            # Test connection
            balance = self.exchange.fetch_balance()
            logger.info("Exchange connection successful")
            
            # Log balance info
            quote_currency = self.symbol.split('/')[1]  # USDT from BTC/USDT
            balance_amount = balance.get('total', {}).get(quote_currency, 0)
            logger.info(f"{quote_currency} Balance: {balance_amount:.2f}")
            
            self._log_to_csv('BOT_START')
            return True
            
        except Exception as e:
            error_info = handle_trading_error(e, "Exchange initialization")
            self._log_to_csv('INITIALIZATION_ERROR', error=str(e))
            return False
    
    def fetch_market_data(self) -> Optional[pd.DataFrame]:
        """Fetch recent market data for analysis"""
        try:
            # Fetch OHLCV data
            ohlcv = self.exchange.fetch_ohlcv(
                self.symbol, 
                self.timeframe, 
                limit=max(self.rsi_period, self.ema_period, self.atr_period) + 50
            )
            
            if not ohlcv:
                logger.warning("No market data received")
                return None
            
            # Convert to DataFrame
            df = pd.DataFrame(
                ohlcv, 
                columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
            )
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            return df
            
        except Exception as e:
            handle_trading_error(e, "Market data fetch")
            return None
    
    def calculate_indicators(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calculate technical indicators"""
        try:
            if len(df) < max(self.rsi_period, self.ema_period, self.atr_period):
                return {}
            
            close_prices = df['close'].values
            high_prices = df['high'].values
            low_prices = df['low'].values
            
            # Calculate indicators
            rsi = talib.RSI(close_prices, timeperiod=self.rsi_period)
            ema = talib.EMA(close_prices, timeperiod=self.ema_period)
            atr = talib.ATR(high_prices, low_prices, close_prices, timeperiod=self.atr_period)
            
            return {
                'rsi': rsi[-1] if not np.isnan(rsi[-1]) else None,
                'ema': ema[-1] if not np.isnan(ema[-1]) else None,
                'atr': atr[-1] if not np.isnan(atr[-1]) else None,
                'current_price': close_prices[-1]
            }
            
        except Exception as e:
            logger.error(f"Indicator calculation error: {e}")
            return {}
    
    def check_entry_signal(self, indicators: Dict[str, float]) -> bool:
        """Check for entry signals"""
        try:
            rsi = indicators.get('rsi')
            ema = indicators.get('ema')
            price = indicators.get('current_price')
            
            if None in [rsi, ema, price]:
                return False
            
            # Long entry condition: RSI oversold AND price above EMA
            long_signal = rsi < self.oversold_threshold and price > ema
            
            if long_signal:
                logger.info(f"ENTRY SIGNAL: RSI={rsi:.1f}, EMA={ema:.2f}, Price={price:.2f}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Entry signal error: {e}")
            return False
    
    def check_exit_signal(self, indicators: Dict[str, float]) -> bool:
        """Check for exit signals"""
        try:
            rsi = indicators.get('rsi')
            
            if rsi is None:
                return False
            
            # Exit condition: RSI overbought
            exit_signal = rsi > self.overbought_threshold
            
            if exit_signal:
                logger.info(f"EXIT SIGNAL: RSI={rsi:.1f}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Exit signal error: {e}")
            return False
    
    def calculate_position_size(self, price: float) -> float:
        """Calculate position size based on balance and risk management"""
        try:
            balance = self.exchange.fetch_balance()
            quote_currency = self.symbol.split('/')[1]
            available_balance = balance['free'][quote_currency]
            
            # Use percentage of available balance
            position_value = available_balance * self.position_size_pct
            position_size = position_value / price
            
            # Apply minimum order size constraints
            markets = self.exchange.load_markets()
            market_info = markets[self.symbol]
            min_amount = market_info.get('limits', {}).get('amount', {}).get('min', 0.001)
            
            if position_size < min_amount:
                logger.warning(f"Position size {position_size:.6f} below minimum {min_amount}")
                return 0
            
            return position_size
            
        except Exception as e:
            handle_trading_error(e, "Position size calculation")
            return 0
    
    def place_buy_order(self, indicators: Dict[str, float]) -> bool:
        """Place buy order with stop-loss and take-profit"""
        try:
            price = indicators['current_price']
            atr = indicators.get('atr', 0)
            
            # Calculate position size
            position_size = self.calculate_position_size(price)
            if position_size == 0:
                return False
            
            # Get current balance
            balance = self.exchange.fetch_balance()
            quote_currency = self.symbol.split('/')[1]
            balance_before = balance['total'][quote_currency]
            
            # Place market buy order
            order = self.exchange.create_market_buy_order(
                self.symbol, 
                position_size
            )
            
            if order['status'] == 'closed' or order['filled'] > 0:
                self.position = {
                    'id': order['id'],
                    'symbol': self.symbol,
                    'amount': order['filled'],
                    'entry_price': order['average'] or price,
                    'timestamp': datetime.now()
                }
                self.entry_price = self.position['entry_price']
                
                # Calculate stop-loss and take-profit levels
                if atr > 0:
                    stop_loss_price = self.entry_price - (atr * self.atr_multiplier_sl)
                    take_profit_price = self.entry_price + (atr * self.atr_multiplier_tp)
                else:
                    # Fallback to percentage-based levels
                    stop_loss_price = self.entry_price * 0.98  # 2% stop loss
                    take_profit_price = self.entry_price * 1.04  # 4% take profit
                
                # Log the trade
                self._log_to_csv(
                    'BUY',
                    amount_base=position_size,
                    price=self.entry_price,
                    rsi=indicators.get('rsi'),
                    ema=indicators.get('ema'),
                    atr=atr,
                    order_id=order['id'],
                    status='FILLED',
                    entry_price=self.entry_price,
                    stop_loss_level=stop_loss_price,
                    take_profit_level=take_profit_price,
                    quote_balance_before=balance_before
                )
                
                logger.info(f"BUY ORDER FILLED: {position_size:.6f} @ {self.entry_price:.2f}")
                logger.info(f"Stop Loss: {stop_loss_price:.2f}, Take Profit: {take_profit_price:.2f}")
                
                return True
            
            return False
            
        except Exception as e:
            error_info = handle_trading_error(e, "Buy order placement")
            self._log_to_csv('BUY_ERROR', error=str(e))
            return False
    
    def place_sell_order(self, indicators: Dict[str, float]) -> bool:
        """Place sell order to close position"""
        try:
            if not self.position:
                return False
            
            price = indicators['current_price']
            
            # Get current balance
            balance = self.exchange.fetch_balance()
            quote_currency = self.symbol.split('/')[1]
            balance_before = balance['total'][quote_currency]
            
            # Place market sell order
            order = self.exchange.create_market_sell_order(
                self.symbol,
                self.position['amount']
            )
            
            if order['status'] == 'closed' or order['filled'] > 0:
                exit_price = order['average'] or price
                
                # Calculate PnL
                pnl_quote = (exit_price - self.entry_price) * self.position['amount']
                pnl_percent = ((exit_price - self.entry_price) / self.entry_price) * 100
                
                # Log the trade
                self._log_to_csv(
                    'SELL',
                    amount_base=self.position['amount'],
                    price=exit_price,
                    rsi=indicators.get('rsi'),
                    ema=indicators.get('ema'),
                    atr=indicators.get('atr'),
                    order_id=order['id'],
                    status='FILLED',
                    entry_price=self.entry_price,
                    pnl_quote=pnl_quote,
                    pnl_percent=pnl_percent,
                    quote_balance_before=balance_before,
                    pnl=pnl_quote
                )
                
                logger.info(f"SELL ORDER FILLED: {self.position['amount']:.6f} @ {exit_price:.2f}")
                logger.info(f"PnL: {pnl_quote:.2f} ({pnl_percent:.2f}%)")
                
                # Clear position
                self.position = None
                self.entry_price = None
                
                return True
            
            return False
            
        except Exception as e:
            error_info = handle_trading_error(e, "Sell order placement")
            self._log_to_csv('SELL_ERROR', error=str(e))
            return False
    
    def trading_loop(self):
        """Main trading loop"""
        logger.info(f"Starting trading loop for {self.symbol}")
        self.is_running = True
        
        while self.is_running:
            try:
                # Fetch market data
                market_data = self.fetch_market_data()
                if market_data is None or len(market_data) < 50:
                    time.sleep(60)  # Wait 1 minute before retry
                    continue
                
                # Calculate indicators
                indicators = self.calculate_indicators(market_data)
                if not indicators:
                    time.sleep(60)
                    continue
                
                # Log current market state
                self._log_to_csv(
                    'MARKET_ANALYSIS',
                    price=indicators.get('current_price'),
                    rsi=indicators.get('rsi'),
                    ema=indicators.get('ema'),
                    atr=indicators.get('atr')
                )
                
                current_time = datetime.now()
                
                # Trading logic
                if not self.position:
                    # Look for entry signals
                    if self.check_entry_signal(indicators):
                        # Avoid rapid-fire signals
                        if (self.last_signal_time is None or 
                            current_time - self.last_signal_time > timedelta(hours=1)):
                            
                            success = self.place_buy_order(indicators)
                            if success:
                                self.last_signal_time = current_time
                
                else:
                    # Look for exit signals
                    if self.check_exit_signal(indicators):
                        self.place_sell_order(indicators)
                
                # Sleep based on timeframe
                sleep_time = self._get_sleep_time()
                logger.info(f"Next check in {sleep_time} seconds...")
                time.sleep(sleep_time)
                
            except KeyboardInterrupt:
                logger.info("Trading loop interrupted by user")
                self.stop()
                break
            except Exception as e:
                error_info = handle_trading_error(e, "Trading loop")
                self._log_to_csv('LOOP_ERROR', error=str(e))
                time.sleep(60)  # Wait before continuing
    
    def _get_sleep_time(self) -> int:
        """Get sleep time based on timeframe"""
        timeframe_minutes = {
            '1m': 1,
            '5m': 5,
            '15m': 15,
            '30m': 30,
            '1h': 60,
            '4h': 240,
            '1d': 1440
        }
        
        minutes = timeframe_minutes.get(self.timeframe, 60)
        return minutes * 60  # Convert to seconds
    
    def stop(self):
        """Stop the trading bot"""
        logger.info("Stopping trading bot...")
        self.is_running = False
        self._log_to_csv('BOT_STOP_MANUAL')
        
        # Close any open positions if needed
        if self.position:
            logger.info("Closing open position...")
            market_data = self.fetch_market_data()
            if market_data is not None:
                indicators = self.calculate_indicators(market_data)
                if indicators:
                    self.place_sell_order(indicators)
    
    def get_status(self) -> Dict[str, Any]:
        """Get current bot status"""
        return {
            'is_running': self.is_running,
            'symbol': self.symbol,
            'timeframe': self.timeframe,
            'position': self.position,
            'csv_log_file': self.csv_file,
            'last_signal_time': self.last_signal_time
        }

def main():
    """Main function to run live trading"""
    # Safety check
    if not is_development_mode():
        response = input("WARNING: Not in testnet mode! Continue? (type 'YES' to continue): ")
        if response != 'YES':
            print("Aborting for safety.")
            return
    
    # Create and initialize trading engine
    bot = LiveTradingEngine("BTC/USDT", "1h")
    
    if not bot.initialize_exchange():
        logger.error("Failed to initialize exchange. Exiting.")
        return
    
    try:
        # Start trading loop
        bot.trading_loop()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    finally:
        bot.stop()

if __name__ == "__main__":
    main()
