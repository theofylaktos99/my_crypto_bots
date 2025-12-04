# 📚 Advanced Trading Strategies Documentation

## Table of Contents
1. [Overview](#overview)
2. [Strategy Descriptions](#strategy-descriptions)
3. [Mathematical Models](#mathematical-models)
4. [Usage Examples](#usage-examples)
5. [Performance Optimization](#performance-optimization)
6. [Risk Management](#risk-management)

---

## Overview

This system includes **7 professional-grade trading strategies** combining technical analysis, machine learning, and advanced mathematical models. Each strategy is designed for different market conditions and risk profiles.

### Strategy Portfolio

| Strategy | Type | Complexity | Best For |
|----------|------|------------|----------|
| RSI-EMA-ATR | Trend Following | ⭐⭐ | Trending markets |
| Z-Score Phi | Mean Reversion | ⭐⭐⭐ | Range-bound markets |
| Advanced Fibonacci | Support/Resistance | ⭐⭐⭐⭐ | Swing trading |
| ML Momentum | Machine Learning | ⭐⭐⭐⭐⭐ | All conditions |
| Bollinger RSI | Volatility | ⭐⭐ | High volatility |
| Moving Average | Trend | ⭐ | Beginner friendly |

---

## Strategy Descriptions

### 1. RSI-EMA-ATR Strategy
**Type**: Trend Following with Momentum
**File**: `rsi_ema_atr_strategy.py`

#### Theory
Combines three powerful indicators:
- **RSI (Relative Strength Index)**: Momentum oscillator
- **EMA (Exponential Moving Average)**: Trend filter
- **ATR (Average True Range)**: Volatility for stop-loss/take-profit

#### Entry Rules
```python
BUY Signal:
- RSI < 30 (oversold)
- Price > EMA(200) (uptrend)
- Volume > Average Volume
- Confidence: 0.7-0.9

SELL Signal:
- RSI > 70 (overbought)
- OR Stop-loss/take-profit hit
```

#### Parameters
```python
{
    'rsi_period': 14,
    'ema_period': 200,
    'atr_period': 14,
    'oversold_threshold': 30,
    'overbought_threshold': 70,
    'atr_stop_multiplier': 1.5,
    'atr_profit_multiplier': 2.0
}
```

---

### 2. Z-Score Phi Strategy
**Type**: Mean Reversion with Golden Ratio
**File**: `zscore_phi_strategy.py`

#### Mathematical Foundation
Uses **Z-Score** analysis combined with the **Golden Ratio (φ = 1.618)**:

```
Z-Score = (Price - μ) / σ
where μ = mean(price), σ = std(price)
```

Golden Ratio Applications:
- Entry threshold: φ = 1.618
- Exit threshold: 1/φ = 0.618

#### Entry Rules
```python
LONG Entry:
- Z-Score < -1.618 (oversold by 1.618 std deviations)
- Momentum ≤ 0 (no upward momentum)
- Volume > Average (confirmation)
- Volatility > 0.01 (sufficient movement)

SHORT Entry:
- Z-Score > +1.618 (overbought)
- Momentum ≥ 0
- Volume > Average

EXIT:
- Z-Score returns to ±0.618 range (mean reversion)
```

#### Why Golden Ratio?
The golden ratio appears naturally in markets through Fibonacci retracements and psychological price levels. Using φ as thresholds provides mathematically optimal entry/exit points.

---

### 3. Advanced Fibonacci Strategy ⭐ NEW
**Type**: Support/Resistance with Multi-Timeframe Analysis
**File**: `advanced_fibonacci_strategy.py`

#### Mathematical Model
**Fibonacci Retracement Levels**:
```
Given: Swing High (H) and Swing Low (L)
Price Range: R = H - L

Fibonacci Levels:
- 0.000: L
- 0.236: L + 0.236R
- 0.382: L + 0.382R  (weak support/resistance)
- 0.500: L + 0.500R  (psychological level)
- 0.618: L + 0.618R  (golden ratio - strong)
- 0.786: L + 0.786R  (very strong)
- 1.000: H
```

**Fibonacci Extensions** (for targets):
```
- 1.272: H + 0.272R
- 1.414: H + 0.414R
- 1.618: H + 0.618R  (primary target)
- 2.000: H + 1.000R
- 2.618: H + 1.618R  (extended target)
```

#### Advanced Features

**1. Automatic Swing Detection**
```python
# Finds local maxima/minima
swing_high = price is highest in window ± 5 bars
swing_low = price is lowest in window ± 5 bars

# Validates swing significance
swing_size = |H - L| / L
if swing_size < 0.02:  # Less than 2%
    discard  # Too small
```

**2. Confluence Analysis**
```python
# Price near Fibonacci level?
def check_confluence(price, fib_levels):
    for level in fib_levels:
        distance = |price - level| / price
        if distance < 0.015:  # Within 1.5%
            return level  # Confluence found
    return None
```

**3. Multi-Indicator Confirmation**
```python
# Requires 3+ bullish signals
bullish_signals = 0

if rsi < 35:           # Oversold
    bullish_signals += 1
if macd > signal:      # Bullish crossover
    bullish_signals += 1
if volume > avg_vol:   # Volume confirmation
    bullish_signals += 1
if price >= fib_618:   # Strong support
    bullish_signals += 1

confidence = bullish_signals / 4.0  # 0.0-1.0

if confidence >= 0.6:  # At least 60%
    GENERATE_BUY_SIGNAL
```

#### Signal Confidence Scoring
```python
Confidence Levels:
- 0.60-0.70: Moderate (3/4 conditions)
- 0.70-0.85: Good (3.5/4 conditions)
- 0.85-1.00: Excellent (4/4 conditions)
```

---

### 4. ML Momentum Strategy ⭐ NEW
**Type**: Machine Learning Enhanced
**File**: `ml_momentum_strategy.py`

#### Machine Learning Architecture

**Ensemble Model**:
```
Final Prediction = (RF_prediction + GB_prediction) / 2

where:
RF = Random Forest Classifier
GB = Gradient Boosting Classifier
```

#### Feature Engineering (20+ Features)

**1. Price-Based Features**
```python
- returns: pct_change()
- log_returns: log(price_t / price_t-1)
- momentum_5, momentum_10, momentum_20
- price_to_sma10, price_to_sma20, price_to_sma50
```

**2. Technical Indicators**
```python
- RSI(14), RSI(7)
- MACD, MACD_signal, MACD_histogram
- Bollinger Bands position
- ATR percentage
- Stochastic oscillator
- Williams %R
- CCI (Commodity Channel Index)
- ADX (Average Directional Index)
```

**3. Volume Features**
```python
- volume_ratio = volume / volume_ma
- money_flow_index
```

**4. Pattern Recognition**
```python
- higher_high, lower_low
- candlestick body_ratio
- upper/lower shadows
```

#### Model Training Process

```python
# 1. Feature Extraction
X = df[feature_columns]  # 20+ features
y = df['target']         # Binary: 0=down, 1=up

# Target Creation
target = 1 if future_price(+5 bars) > current_price else 0

# 2. Data Preprocessing
X_scaled = StandardScaler().fit_transform(X)

# 3. Train Ensemble
RandomForest(n_estimators=100, max_depth=10)
GradientBoosting(n_estimators=100, learning_rate=0.1)

# 4. Prediction
rf_prob = RF.predict_proba(X_current)
gb_prob = GB.predict_proba(X_current)
ensemble_prob = (rf_prob + gb_prob) / 2

# 5. Signal Generation
if ensemble_prob[UP] > threshold:
    BUY_SIGNAL (confidence = ensemble_prob[UP])
```

#### Adaptive Retraining
```python
# Retrain every N candles to adapt to market changes
if data_points % retrain_interval == 0:
    retrain_models()
```

#### Feature Importance Analysis
The model tracks which features are most predictive:
```python
top_features = {
    'momentum_20': 0.15,
    'rsi': 0.12,
    'macd_histogram': 0.11,
    'price_to_sma20': 0.10,
    'volume_ratio': 0.09,
    ...
}
```

---

## Mathematical Models

### Portfolio Optimization

**1. Sharpe Ratio Maximization**
```
Maximize: Sharpe = (R_p - R_f) / σ_p

where:
R_p = Portfolio return
R_f = Risk-free rate
σ_p = Portfolio standard deviation

Subject to:
Σ w_i = 1  (weights sum to 1)
0 ≤ w_i ≤ 1  (long-only constraint)
```

**2. Kelly Criterion**
```
Optimal Position Size:
f* = (p × b - q) / b

where:
p = win rate
q = 1 - p (loss rate)
b = win/loss ratio

Conservative Kelly = f* × 0.25  (quarter Kelly)
```

**3. Value at Risk (VaR)**
```
VaR_α = -Quantile(Returns, 1-α)

For 95% confidence:
VaR_0.95 = -Percentile(Returns, 5%)

Interpretation: 95% confident losses won't exceed VaR
```

**4. Monte Carlo Simulation**
```python
# Simulate 10,000 possible futures
for i in range(10000):
    # Generate random returns
    returns = np.random.normal(μ, σ, horizon)
    
    # Calculate cumulative return
    final_value = (1 + returns).prod()
    simulations.append(final_value)

# Analyze distribution
percentile_5 = np.percentile(simulations, 5)   # Worst case
percentile_95 = np.percentile(simulations, 95)  # Best case
probability_profit = sum(s > 1.0) / 10000
```

---

## Usage Examples

### Example 1: Using Advanced Fibonacci Strategy

```python
from src.strategies import AdvancedFibonacciStrategy

# Initialize strategy
config = {
    'name': 'Fibonacci Strategy',
    'lookback_period': 50,
    'min_swing_size': 0.02,  # 2% minimum swing
    'confluence_threshold': 0.015,  # 1.5% price range
    'volume_confirmation': True
}

strategy = AdvancedFibonacciStrategy(config)

# Generate signal
signal = strategy.generate_signal(market_data)

if signal:
    print(f"Action: {signal.action}")
    print(f"Confidence: {signal.confidence:.2%}")
    print(f"Fibonacci Level: {signal.metadata['fib_level']}")
    print(f"Stop Loss: {signal.metadata['stop_loss']}")
    print(f"Take Profit: {signal.metadata['take_profit']}")
```

### Example 2: Using ML Momentum Strategy

```python
from src.strategies import MLMomentumStrategy

# Initialize
config = {
    'name': 'ML Momentum',
    'lookback_period': 100,
    'prediction_threshold': 0.6,
    'retrain_interval': 500,
    'feature_engineering': True
}

ml_strategy = MLMomentumStrategy(config)

# Train on historical data
ml_strategy.train_models(historical_data)

# Get model info
model_info = ml_strategy.get_model_info()
print(f"Training samples: {model_info['training_samples']}")
print(f"Top features: {model_info['top_features']}")

# Generate prediction
signal = ml_strategy.generate_signal(market_data)

if signal:
    print(f"ML Prediction: {signal.metadata['ml_prediction']}")
    print(f"Confidence: {signal.confidence:.2%}")
    print(f"Random Forest prob: {signal.metadata['rf_prob']:.2%}")
    print(f"Gradient Boost prob: {signal.metadata['gb_prob']:.2%}")
```

### Example 3: Portfolio Optimization

```python
from src.utils.portfolio_optimizer import PortfolioOptimizer

# Initialize optimizer
optimizer = PortfolioOptimizer(risk_free_rate=0.02)

# Optimize for maximum Sharpe ratio
weights, metrics = optimizer.optimize_sharpe_ratio(returns_data)

print(f"Optimal Weights: {weights}")
print(f"Expected Return: {metrics['return']:.2%}")
print(f"Volatility: {metrics['volatility']:.2%}")
print(f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
print(f"Max Drawdown: {metrics['max_drawdown']:.2%}")

# Calculate Kelly Criterion position size
kelly_size = optimizer.kelly_criterion(
    win_rate=0.55,
    win_loss_ratio=1.5,
    conservative_factor=0.25
)
print(f"Kelly Position Size: {kelly_size:.2%}")

# Run Monte Carlo simulation
mc_results = optimizer.monte_carlo_simulation(
    returns_data, 
    weights, 
    n_simulations=10000,
    horizon=252
)
print(f"Mean final value: {mc_results['mean_final_value']:.2f}")
print(f"Probability of profit: {mc_results['probability_profit']:.2%}")
```

---

## Performance Optimization

### 1. Vectorization
```python
# Bad: Loop over data
for i in range(len(data)):
    rsi[i] = calculate_rsi(data[:i])

# Good: Vectorized operation
rsi = calculate_rsi(data)  # Operates on entire array
```

### 2. Caching
```python
# Cache expensive calculations
@lru_cache(maxsize=128)
def calculate_indicators(data_hash):
    return compute_all_indicators(data)
```

### 3. Parallel Processing
```python
from multiprocessing import Pool

# Run backtests in parallel
with Pool() as pool:
    results = pool.map(backtest_strategy, strategies)
```

---

## Risk Management

### Position Sizing Framework

**1. Percentage Risk Method**
```python
risk_per_trade = 0.02  # 2% of capital
account_balance = 10000
entry_price = 50000
stop_loss = 48000

risk_amount = account_balance * risk_per_trade  # $200
price_risk = entry_price - stop_loss  # $2000
position_size = risk_amount / price_risk  # 0.1 BTC
```

**2. Kelly Criterion**
```python
# Historical performance
win_rate = 0.55  # 55% wins
avg_win = 300
avg_loss = 200
win_loss_ratio = avg_win / avg_loss  # 1.5

# Calculate Kelly
kelly = (0.55 * 1.5 - 0.45) / 1.5  # 0.25
conservative_kelly = kelly * 0.25  # 0.0625 (6.25%)
```

**3. Volatility Adjusted**
```python
base_position = 0.05  # 5%
current_volatility = calculate_atr(data)
average_volatility = historical_atr.mean()

adjusted_position = base_position * (average_volatility / current_volatility)
```

### Stop-Loss Strategies

**1. ATR-Based**
```python
atr = calculate_atr(data, period=14)
stop_loss = entry_price - (atr * 1.5)  # 1.5x ATR
```

**2. Fibonacci-Based**
```python
# Use next Fibonacci level below entry
fib_levels = calculate_fibonacci(swing_high, swing_low)
stop_loss = fib_levels['0.618']  # Strong support
```

**3. Percentage-Based**
```python
stop_loss = entry_price * 0.98  # 2% stop
```

### Risk Metrics to Monitor

```python
# Daily metrics
daily_pnl = calculate_daily_pnl()
max_daily_loss_limit = capital * 0.05  # 5% max

# Position-level
total_exposure = sum(position_values)
max_exposure_limit = capital * 1.0  # No leverage

# Strategy-level
strategy_var = calculate_var(strategy_returns, confidence=0.95)
strategy_sharpe = calculate_sharpe(strategy_returns)
```

---

## Best Practices

### 1. Strategy Selection
- **Trending markets**: RSI-EMA-ATR, ML Momentum
- **Range-bound**: Z-Score Phi, Bollinger RSI
- **Swing trading**: Advanced Fibonacci
- **All conditions**: ML Momentum (adapts)

### 2. Diversification
- Use 3-5 uncorrelated strategies
- Check correlation matrix regularly
- Rebalance when correlation > 0.7

### 3. Testing
- Backtest on minimum 2 years data
- Out-of-sample testing (30% holdout)
- Walk-forward optimization
- Monte Carlo validation

### 4. Monitoring
- Track Sharpe ratio (target > 1.5)
- Monitor max drawdown (< 20%)
- Check win rate (> 50% ideal)
- Validate profit factor (> 1.5)

---

## Advanced Topics

### Multi-Timeframe Analysis
```python
# Confirm signals across timeframes
def multi_timeframe_signal(symbol):
    signal_15m = strategy.generate_signal(get_data(symbol, '15m'))
    signal_1h = strategy.generate_signal(get_data(symbol, '1h'))
    signal_4h = strategy.generate_signal(get_data(symbol, '4h'))
    
    # All timeframes agree?
    if signal_15m.action == signal_1h.action == signal_4h.action:
        return Signal(
            action=signal_1h.action,
            confidence=min(s.confidence for s in [signal_15m, signal_1h, signal_4h])
        )
```

### Regime Detection
```python
def detect_market_regime(data):
    volatility = data['close'].pct_change().std()
    trend_strength = abs(data['close'].ewm(span=20).mean().pct_change().mean())
    
    if volatility > 0.03:
        return 'high_volatility'
    elif trend_strength > 0.01:
        return 'trending'
    else:
        return 'ranging'

# Adapt strategy to regime
regime = detect_market_regime(data)
if regime == 'trending':
    use_trend_following_strategy()
elif regime == 'ranging':
    use_mean_reversion_strategy()
```

---

## Conclusion

This advanced strategy suite combines:
- ✅ Classical technical analysis
- ✅ Modern machine learning
- ✅ Mathematical optimization
- ✅ Professional risk management
- ✅ Real-time adaptation

Each strategy is production-ready with comprehensive error handling, logging, and performance tracking.

**For support**: Open an issue on GitHub
**For updates**: Check CHANGELOG.md

---

*Last Updated: December 2025*
*Version: 2.0.0*
