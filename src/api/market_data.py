# market_data.py - Unified Market Data Fetcher
import requests
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class MarketDataFetcher:
    """Unified market data fetcher supporting multiple sources"""
    
    def __init__(self):
        self.coingecko_base = "https://api.coingecko.com/api/v3"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'CryptoTradingBot/1.0'
        })
    
    def get_live_market_data(self, limit: int = 20) -> Dict:
        """Get live market data from CoinGecko"""
        try:
            url = f"{self.coingecko_base}/coins/markets"
            params = {
                'vs_currency': 'usd',
                'order': 'market_cap_desc',
                'per_page': limit,
                'page': 1,
                'sparkline': 'false',
                'price_change_percentage': '24h,7d,30d'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            market_data = {}
            
            for crypto in data:
                symbol = crypto['symbol'].upper()
                market_data[symbol] = {
                    'name': crypto['name'],
                    'symbol': symbol,
                    'price': crypto.get('current_price', 0),
                    'change_24h': crypto.get('price_change_percentage_24h', 0),
                    'change_7d': crypto.get('price_change_percentage_7d', 0),
                    'change_30d': crypto.get('price_change_percentage_30d', 0),
                    'market_cap': crypto.get('market_cap', 0),
                    'volume_24h': crypto.get('total_volume', 0),
                    'rank': crypto.get('market_cap_rank', 0),
                    'last_updated': datetime.now().isoformat()
                }
            
            logger.info(f"✅ Fetched data for {len(market_data)} cryptocurrencies")
            return market_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Network error fetching market data: {e}")
            return {}
        except Exception as e:
            logger.error(f"❌ Error processing market data: {e}")
            return {}
    
    def get_price_history(self, symbol: str, days: int = 30) -> pd.DataFrame:
        """Get historical price data"""
        try:
            # Convert symbol to CoinGecko ID format
            coin_id = self._get_coin_id(symbol)
            if not coin_id:
                return pd.DataFrame()
            
            url = f"{self.coingecko_base}/coins/{coin_id}/market_chart"
            params = {
                'vs_currency': 'usd',
                'days': days,
                'interval': 'daily' if days > 90 else 'hourly'
            }
            
            response = self.session.get(url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            # Process the data
            prices = data.get('prices', [])
            volumes = data.get('total_volumes', [])
            
            df = pd.DataFrame(prices, columns=['timestamp', 'price'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            if volumes:
                volume_df = pd.DataFrame(volumes, columns=['timestamp', 'volume'])
                volume_df['timestamp'] = pd.to_datetime(volume_df['timestamp'], unit='ms')
                df = df.merge(volume_df, on='timestamp', how='left')
            
            df.set_index('timestamp', inplace=True)
            
            logger.info(f"✅ Fetched {len(df)} historical data points for {symbol}")
            return df
            
        except Exception as e:
            logger.error(f"❌ Error fetching price history for {symbol}: {e}")
            return pd.DataFrame()
    
    def _get_coin_id(self, symbol: str) -> Optional[str]:
        """Convert symbol to CoinGecko coin ID"""
        symbol_map = {
            'BTC': 'bitcoin',
            'ETH': 'ethereum', 
            'BNB': 'binancecoin',
            'ADA': 'cardano',
            'DOT': 'polkadot',
            'MATIC': 'polygon',
            'SOL': 'solana',
            'LINK': 'chainlink',
            'UNI': 'uniswap'
        }
        
        return symbol_map.get(symbol.upper())
    
    def get_trending_coins(self) -> Dict:
        """Get trending cryptocurrencies"""
        try:
            url = f"{self.coingecko_base}/search/trending"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            trending = {}
            
            for item in data.get('coins', []):
                coin = item.get('item', {})
                trending[coin.get('symbol', '').upper()] = {
                    'name': coin.get('name', ''),
                    'rank': coin.get('market_cap_rank', 0),
                    'score': coin.get('score', 0)
                }
            
            return trending
            
        except Exception as e:
            logger.error(f"❌ Error fetching trending coins: {e}")
            return {}
    
    def get_fear_greed_index(self) -> Dict:
        """Get Fear & Greed Index (if available)"""
        try:
            # This is a placeholder - you can integrate with actual F&G API
            return {
                'value': np.random.randint(20, 80),
                'classification': 'Neutral',
                'last_updated': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"❌ Error fetching Fear & Greed Index: {e}")
            return {}
