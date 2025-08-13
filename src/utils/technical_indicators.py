# technical_indicators.py - Alternative Technical Analysis Functions
import pandas as pd
import numpy as np
from typing import Union, Optional

def RSI(prices: Union[pd.Series, np.ndarray], timeperiod: int = 14) -> pd.Series:
    """
    Calculate RSI (Relative Strength Index)
    Alternative to talib.RSI
    """
    if isinstance(prices, np.ndarray):
        prices = pd.Series(prices)
    
    delta = prices.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    avg_gain = gain.rolling(window=timeperiod).mean()
    avg_loss = loss.rolling(window=timeperiod).mean()
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi

def EMA(prices: Union[pd.Series, np.ndarray], timeperiod: int = 14) -> pd.Series:
    """
    Calculate EMA (Exponential Moving Average)
    Alternative to talib.EMA
    """
    if isinstance(prices, np.ndarray):
        prices = pd.Series(prices)
    
    return prices.ewm(span=timeperiod, adjust=False).mean()

def SMA(prices: Union[pd.Series, np.ndarray], timeperiod: int = 14) -> pd.Series:
    """
    Calculate SMA (Simple Moving Average)
    Alternative to talib.SMA
    """
    if isinstance(prices, np.ndarray):
        prices = pd.Series(prices)
    
    return prices.rolling(window=timeperiod).mean()

def ATR(high: Union[pd.Series, np.ndarray], 
        low: Union[pd.Series, np.ndarray], 
        close: Union[pd.Series, np.ndarray], 
        timeperiod: int = 14) -> pd.Series:
    """
    Calculate ATR (Average True Range)
    Alternative to talib.ATR
    """
    if isinstance(high, np.ndarray):
        high = pd.Series(high)
    if isinstance(low, np.ndarray):
        low = pd.Series(low)
    if isinstance(close, np.ndarray):
        close = pd.Series(close)
    
    high_low = high - low
    high_close_prev = abs(high - close.shift(1))
    low_close_prev = abs(low - close.shift(1))
    
    true_range = pd.concat([high_low, high_close_prev, low_close_prev], axis=1).max(axis=1)
    atr = true_range.rolling(window=timeperiod).mean()
    
    return atr

def BBANDS(prices: Union[pd.Series, np.ndarray], 
           timeperiod: int = 20, 
           nbdevup: float = 2, 
           nbdevdn: float = 2) -> tuple:
    """
    Calculate Bollinger Bands
    Returns: (upperband, middleband, lowerband)
    """
    if isinstance(prices, np.ndarray):
        prices = pd.Series(prices)
    
    middle = prices.rolling(window=timeperiod).mean()
    std = prices.rolling(window=timeperiod).std()
    
    upper = middle + (std * nbdevup)
    lower = middle - (std * nbdevdn)
    
    return upper, middle, lower

def MACD(prices: Union[pd.Series, np.ndarray], 
         fastperiod: int = 12, 
         slowperiod: int = 26, 
         signalperiod: int = 9) -> tuple:
    """
    Calculate MACD
    Returns: (macd, macdsignal, macdhist)
    """
    if isinstance(prices, np.ndarray):
        prices = pd.Series(prices)
    
    ema_fast = EMA(prices, fastperiod)
    ema_slow = EMA(prices, slowperiod)
    
    macd = ema_fast - ema_slow
    signal = EMA(macd, signalperiod)
    histogram = macd - signal
    
    return macd, signal, histogram

def STOCH(high: Union[pd.Series, np.ndarray],
          low: Union[pd.Series, np.ndarray],
          close: Union[pd.Series, np.ndarray],
          fastk_period: int = 14,
          slowk_period: int = 3,
          slowd_period: int = 3) -> tuple:
    """
    Calculate Stochastic Oscillator
    Returns: (slowk, slowd)
    """
    if isinstance(high, np.ndarray):
        high = pd.Series(high)
    if isinstance(low, np.ndarray):
        low = pd.Series(low)
    if isinstance(close, np.ndarray):
        close = pd.Series(close)
    
    lowest_low = low.rolling(window=fastk_period).min()
    highest_high = high.rolling(window=fastk_period).max()
    
    fastk = 100 * (close - lowest_low) / (highest_high - lowest_low)
    slowk = fastk.rolling(window=slowk_period).mean()
    slowd = slowk.rolling(window=slowd_period).mean()
    
    return slowk, slowd

def WILLIAMS_R(high: Union[pd.Series, np.ndarray],
               low: Union[pd.Series, np.ndarray], 
               close: Union[pd.Series, np.ndarray],
               timeperiod: int = 14) -> pd.Series:
    """
    Calculate Williams %R
    """
    if isinstance(high, np.ndarray):
        high = pd.Series(high)
    if isinstance(low, np.ndarray):
        low = pd.Series(low)
    if isinstance(close, np.ndarray):
        close = pd.Series(close)
    
    highest_high = high.rolling(window=timeperiod).max()
    lowest_low = low.rolling(window=timeperiod).min()
    
    williams_r = -100 * (highest_high - close) / (highest_high - lowest_low)
    
    return williams_r

# Compatibility aliases for easier migration from talib
def talib_RSI(prices, timeperiod=14):
    """Compatibility function for talib.RSI"""
    return RSI(prices, timeperiod)

def talib_EMA(prices, timeperiod=14):
    """Compatibility function for talib.EMA"""
    return EMA(prices, timeperiod)

def talib_SMA(prices, timeperiod=14):
    """Compatibility function for talib.SMA"""
    return SMA(prices, timeperiod)

def talib_ATR(high, low, close, timeperiod=14):
    """Compatibility function for talib.ATR"""
    return ATR(high, low, close, timeperiod)
