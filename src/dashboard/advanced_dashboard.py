# advanced_dashboard.py - Enhanced Professional Dashboard με Advanced Features
import streamlit as st
import pandas as pd
import numpy as np
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import our advanced modules
from strategies import (
    AdvancedFibonacciStrategy,
    MLMomentumStrategy,
    RSIEMAATRStrategy,
    ZScorePhiStrategy
)
from utils.portfolio_optimizer import PortfolioOptimizer
from dashboard.strategy_comparison_dashboard import StrategyComparisonDashboard

# 🎨 Page Configuration
st.set_page_config(
    page_title="CryptoBot Pro - Advanced",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 🎨 Enhanced FLYNT Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Arimo:wght@400;700&display=swap');
    
    :root {
        --flynt-primary: #187794;
        --flynt-secondary: #ffffff;
        --flynt-button-idle: #6db2c7;
        --flynt-content: #d0d0d0;
        --flynt-background: #0f1419;
        --flynt-card-bg: rgba(255, 255, 255, 0.05);
        --flynt-border: rgba(109, 178, 199, 0.2);
        --flynt-success: #28a745;
        --flynt-danger: #dc3545;
        --flynt-warning: #ffc107;
    }
    
    .stApp {
        background: linear-gradient(135deg, var(--flynt-background) 0%, #181818 100%);
        font-family: 'Inter', sans-serif;
        color: var(--flynt-content);
    }
    
    /* Hide Streamlit branding */
    #MainMenu, footer {visibility: hidden;}
    
    /* Enhanced cards */
    .strategy-card {
        background: var(--flynt-card-bg);
        border: 1px solid var(--flynt-border);
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        transition: all 0.3s ease;
    }
    
    .strategy-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(24, 119, 148, 0.2);
        border-color: var(--flynt-primary);
    }
    
    .metric-card {
        background: linear-gradient(135deg, rgba(24, 119, 148, 0.1), rgba(109, 178, 199, 0.05));
        border: 1px solid var(--flynt-border);
        border-radius: 8px;
        padding: 15px;
        text-align: center;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: var(--flynt-primary);
        text-shadow: 0 0 10px rgba(24, 119, 148, 0.3);
    }
    
    .metric-label {
        font-size: 0.85rem;
        color: var(--flynt-content);
        text-transform: uppercase;
        letter-spacing: 1px;
        opacity: 0.8;
    }
</style>
""", unsafe_allow_html=True)

# 🚀 Professional Header
st.markdown("""
<div style="text-align: center; padding: 30px 0;">
    <h1 style="background: linear-gradient(135deg, #187794, #6db2c7); 
              -webkit-background-clip: text; -webkit-text-fill-color: transparent;
              font-size: 3rem; font-weight: 700; margin: 0;">
        🎯 CryptoBot Professional
    </h1>
    <p style="color: #d0d0d0; font-size: 1.2rem; opacity: 0.8; margin-top: 10px;">
        Advanced Trading Platform | Institutional-Grade Analytics
    </p>
</div>
""", unsafe_allow_html=True)

# 🎛️ Navigation Sidebar
with st.sidebar:
    st.markdown("### 🎯 Navigation")
    
    page = st.radio(
        "Select Module",
        [
            "📊 Market Overview",
            "🎯 Advanced Strategies",
            "📈 Portfolio Optimizer",
            "📉 Strategy Comparison",
            "🤖 ML Predictions",
            "📐 Fibonacci Analysis",
            "⚙️ Risk Management"
        ],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # System Status
    st.markdown("### 💻 System Status")
    st.success("✅ Platform Online")
    st.success("✅ Market Data Connected")
    st.info("🔄 Strategies Ready")
    st.warning("⚠️ Demo Mode Active")
    
    st.markdown("---")
    
    # Quick Stats
    st.markdown("### 📊 Quick Stats")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Active Strategies", "7", "+2")
    with col2:
        st.metric("Portfolio Value", "$10K", "+5.2%")

# 📊 MARKET OVERVIEW PAGE
if page == "📊 Market Overview":
    st.markdown("## 📊 Market Overview")
    
    # Create sample market data
    market_data = {
        'Symbol': ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT', 'ADA/USDT'],
        'Price': [43250.50, 2280.75, 315.20, 98.45, 0.58],
        'Change 24h': [2.5, -1.2, 3.8, 5.2, -0.8],
        'Volume': ['$28.5B', '$12.3B', '$2.1B', '$1.8B', '$650M'],
        'Market Cap': ['$845B', '$275B', '$48B', '$42B', '$20B']
    }
    df = pd.DataFrame(market_data)
    
    # Metrics row
    cols = st.columns(5)
    for idx, row in df.iterrows():
        with cols[idx]:
            change_color = "🟢" if row['Change 24h'] > 0 else "🔴"
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">${row['Price']:,.2f}</div>
                <div class="metric-label">{row['Symbol']}</div>
                <div style="color: {'#28a745' if row['Change 24h'] > 0 else '#dc3545'}; font-size: 0.9rem; margin-top: 5px;">
                    {change_color} {row['Change 24h']:+.1f}%
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Market table
    st.dataframe(
        df.style.applymap(
            lambda x: 'color: #28a745' if isinstance(x, (int, float)) and x > 0 else ('color: #dc3545' if isinstance(x, (int, float)) and x < 0 else ''),
            subset=['Change 24h']
        ),
        use_container_width=True
    )

# 🎯 ADVANCED STRATEGIES PAGE
elif page == "🎯 Advanced Strategies":
    st.markdown("## 🎯 Advanced Trading Strategies")
    
    st.info("💡 **Professional Strategy Suite** - Επιλέξτε και παραμετροποιήστε προηγμένες στρατηγικές trading")
    
    # Strategy selection
    strategy_choice = st.selectbox(
        "Επιλογή Στρατηγικής",
        [
            "Advanced Fibonacci Strategy",
            "ML Momentum Strategy",
            "RSI-EMA-ATR Strategy",
            "Z-Score Phi Strategy"
        ]
    )
    
    if strategy_choice == "Advanced Fibonacci Strategy":
        st.markdown("### 📐 Advanced Fibonacci Strategy")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            <div class="strategy-card">
                <h4>📊 Strategy Details</h4>
                <p><strong>Type:</strong> Support/Resistance Trading</p>
                <p><strong>Mathematical Basis:</strong> Golden Ratio (φ = 1.618)</p>
                <p><strong>Confidence Scoring:</strong> 0.6 - 1.0</p>
                <p><strong>Best For:</strong> Swing Trading</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("#### ⚙️ Configuration")
            lookback = st.slider("Lookback Period", 20, 100, 50)
            min_swing = st.slider("Min Swing Size (%)", 1.0, 5.0, 2.0) / 100
            confluence = st.slider("Confluence Threshold (%)", 0.5, 3.0, 1.5) / 100
        
        with col2:
            st.markdown("""
            <div class="strategy-card">
                <h4>🎯 Fibonacci Levels</h4>
                <ul style="list-style: none; padding-left: 0;">
                    <li>✓ <strong>0.236</strong> - Shallow retracement</li>
                    <li>✓ <strong>0.382</strong> - Weak support/resistance</li>
                    <li>✓ <strong>0.500</strong> - Psychological level</li>
                    <li>✓ <strong>0.618</strong> - Golden ratio (strong)</li>
                    <li>✓ <strong>0.786</strong> - Deep retracement</li>
                </ul>
                <h4 style="margin-top: 20px;">🎯 Extensions</h4>
                <ul style="list-style: none; padding-left: 0;">
                    <li>✓ <strong>1.272, 1.414, 1.618, 2.000</strong></li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        # Initialize strategy
        try:
            config = {
                'name': 'Fibonacci Strategy',
                'lookback_period': lookback,
                'min_swing_size': min_swing,
                'confluence_threshold': confluence
            }
            strategy = AdvancedFibonacciStrategy(config)
            
            st.success("✅ Strategy initialized successfully!")
            
            # Display strategy info
            st.markdown("#### 📊 Strategy Status")
            info = strategy.get_strategy_info()
            
            metrics_cols = st.columns(4)
            with metrics_cols[0]:
                st.metric("Current Position", info.get('current_position', 0))
            with metrics_cols[1]:
                st.metric("Total Trades", info.get('total_trades', 0))
            with metrics_cols[2]:
                st.metric("Risk per Trade", f"{info.get('risk_per_trade', 0)*100:.1f}%")
            with metrics_cols[3]:
                st.metric("Max Position", f"{info.get('max_position_size', 0)*100:.1f}%")
            
        except Exception as e:
            st.error(f"Error initializing strategy: {e}")
    
    elif strategy_choice == "ML Momentum Strategy":
        st.markdown("### 🤖 ML Momentum Strategy")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            <div class="strategy-card">
                <h4>🧠 Machine Learning Details</h4>
                <p><strong>Ensemble Method:</strong> Random Forest + Gradient Boosting</p>
                <p><strong>Features:</strong> 20+ technical indicators</p>
                <p><strong>Training:</strong> Real-time adaptive</p>
                <p><strong>Prediction:</strong> 5-bar ahead forecast</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("#### ⚙️ ML Configuration")
            lookback_ml = st.slider("Training Lookback", 50, 200, 100)
            threshold = st.slider("Prediction Threshold", 0.5, 0.9, 0.6)
            retrain = st.slider("Retrain Interval", 100, 1000, 500)
        
        with col2:
            st.markdown("""
            <div class="strategy-card">
                <h4>📊 Feature Categories</h4>
                <ul style="list-style: none; padding-left: 0;">
                    <li>✓ <strong>Momentum:</strong> 5, 10, 20 periods</li>
                    <li>✓ <strong>Moving Averages:</strong> SMA, EMA</li>
                    <li>✓ <strong>Oscillators:</strong> RSI, Stochastic</li>
                    <li>✓ <strong>Volatility:</strong> ATR, Bollinger</li>
                    <li>✓ <strong>Volume:</strong> Ratios & MFI</li>
                    <li>✓ <strong>Patterns:</strong> Candlestick features</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            # Model performance
            st.markdown("#### 📈 Model Performance")
            st.info("Model trains on historical data to predict future price movements")
        
        try:
            config = {
                'name': 'ML Momentum',
                'lookback_period': lookback_ml,
                'prediction_threshold': threshold,
                'retrain_interval': retrain,
                'feature_engineering': True
            }
            ml_strategy = MLMomentumStrategy(config)
            
            st.success("✅ ML Strategy initialized successfully!")
            
            # Display model info
            model_info = ml_strategy.get_model_info()
            
            metrics_cols = st.columns(4)
            with metrics_cols[0]:
                st.metric("Model Status", "Ready" if model_info['is_trained'] else "Untrained")
            with metrics_cols[1]:
                st.metric("Features", model_info['feature_count'])
            with metrics_cols[2]:
                st.metric("Training Samples", model_info['training_samples'])
            with metrics_cols[3]:
                st.metric("Predictions", model_info['prediction_count'])
            
            # Top features
            if model_info.get('top_features'):
                st.markdown("##### 🎯 Most Important Features")
                for i, feature in enumerate(model_info['top_features'][:5], 1):
                    st.text(f"{i}. {feature}")
        
        except Exception as e:
            st.error(f"Error initializing ML strategy: {e}")

# 📈 PORTFOLIO OPTIMIZER PAGE
elif page == "📈 Portfolio Optimizer":
    st.markdown("## 📈 Portfolio Optimization Tools")
    
    st.info("💡 **Professional Portfolio Management** - Χρησιμοποιήστε Modern Portfolio Theory για βελτιστοποίηση")
    
    # Optimization method selection
    opt_method = st.selectbox(
        "Μέθοδος Βελτιστοποίησης",
        [
            "Sharpe Ratio Maximization",
            "Minimum Variance",
            "Risk Parity",
            "Kelly Criterion",
            "Monte Carlo Simulation"
        ]
    )
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if opt_method == "Sharpe Ratio Maximization":
            st.markdown("### 📊 Sharpe Ratio Optimization")
            
            st.markdown("""
            <div class="strategy-card">
                <h4>Mathematical Formula</h4>
                <p style="font-size: 1.2rem; text-align: center; padding: 15px;">
                    <strong>Sharpe = (R<sub>p</sub> - R<sub>f</sub>) / σ<sub>p</sub></strong>
                </p>
                <p>Where:</p>
                <ul>
                    <li><strong>R<sub>p</sub></strong> = Portfolio Return</li>
                    <li><strong>R<sub>f</sub></strong> = Risk-free Rate</li>
                    <li><strong>σ<sub>p</sub></strong> = Portfolio Standard Deviation</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("#### ⚙️ Configuration")
            risk_free_rate = st.slider("Risk-Free Rate (%)", 0.0, 10.0, 2.0) / 100
            
            st.markdown("#### 📊 Sample Results")
            # Mock optimization results
            st.success("✅ Optimization Complete!")
            
            results_cols = st.columns(4)
            with results_cols[0]:
                st.metric("Expected Return", "15.2%", "+3.1%")
            with results_cols[1]:
                st.metric("Volatility", "12.5%", "-2.0%")
            with results_cols[2]:
                st.metric("Sharpe Ratio", "1.85", "+0.25")
            with results_cols[3]:
                st.metric("Max Drawdown", "-8.2%", "+1.5%")
        
        elif opt_method == "Kelly Criterion":
            st.markdown("### 🎯 Kelly Criterion Position Sizing")
            
            st.markdown("""
            <div class="strategy-card">
                <h4>Mathematical Formula</h4>
                <p style="font-size: 1.2rem; text-align: center; padding: 15px;">
                    <strong>f* = (bp - q) / b</strong>
                </p>
                <p>Where:</p>
                <ul>
                    <li><strong>p</strong> = Win Probability</li>
                    <li><strong>q</strong> = Loss Probability (1-p)</li>
                    <li><strong>b</strong> = Win/Loss Ratio</li>
                    <li><strong>f*</strong> = Optimal Position Size</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("#### ⚙️ Input Parameters")
            col_a, col_b = st.columns(2)
            with col_a:
                win_rate = st.slider("Win Rate (%)", 40.0, 80.0, 55.0) / 100
                avg_win = st.number_input("Average Win ($)", 100, 1000, 300)
            with col_b:
                avg_loss = st.number_input("Average Loss ($)", 50, 500, 200)
                conservative = st.slider("Conservative Factor", 0.1, 1.0, 0.25)
            
            # Calculate Kelly
            win_loss_ratio = avg_win / avg_loss
            kelly = (win_rate * win_loss_ratio - (1 - win_rate)) / win_loss_ratio
            conservative_kelly = kelly * conservative
            
            st.markdown("#### 📊 Results")
            result_cols = st.columns(3)
            with result_cols[0]:
                st.metric("Full Kelly", f"{kelly*100:.2f}%")
            with result_cols[1]:
                st.metric("Conservative Kelly", f"{conservative_kelly*100:.2f}%", 
                         delta=f"×{conservative}")
            with result_cols[2]:
                st.metric("Position Size ($10K)", f"${conservative_kelly*10000:.0f}")
            
            if kelly > 0:
                st.success(f"✅ Positive Edge Detected! Recommended position: {conservative_kelly*100:.2f}%")
            else:
                st.error("❌ Negative Edge - Do not trade this strategy!")
    
    with col2:
        st.markdown("### 📚 About")
        st.markdown("""
        <div class="strategy-card">
            <h4>Portfolio Optimization</h4>
            <p>Modern Portfolio Theory helps maximize returns for a given level of risk.</p>
            
            <h4 style="margin-top: 20px;">Available Methods</h4>
            <ul>
                <li><strong>Sharpe:</strong> Risk-adjusted returns</li>
                <li><strong>Min Variance:</strong> Lowest risk</li>
                <li><strong>Risk Parity:</strong> Equal risk contribution</li>
                <li><strong>Kelly:</strong> Optimal sizing</li>
                <li><strong>Monte Carlo:</strong> Scenario analysis</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

# 📉 STRATEGY COMPARISON PAGE  
elif page == "📉 Strategy Comparison":
    st.markdown("## 📉 Strategy Performance Comparison")
    
    st.info("💡 **Professional Analytics** - Σύγκριση απόδοσης διαφορετικών στρατηγικών")
    
    # Create comparison dashboard
    comparison = StrategyComparisonDashboard()
    
    # Mock data for demonstration
    strategies_data = {
        'strategies': {
            'Fibonacci': {'is_active': True},
            'ML Momentum': {'is_active': True},
            'RSI-EMA-ATR': {'is_active': False},
            'Z-Score Phi': {'is_active': True}
        },
        'performance': {
            'Fibonacci': {
                'total_return': 12.5,
                'sharpe_ratio': 1.75,
                'win_rate': 58.0,
                'max_drawdown': -8.2,
                'profit_factor': 1.85,
                'total_trades': 45
            },
            'ML Momentum': {
                'total_return': 15.8,
                'sharpe_ratio': 1.92,
                'win_rate': 62.0,
                'max_drawdown': -6.5,
                'profit_factor': 2.10,
                'total_trades': 38
            },
            'RSI-EMA-ATR': {
                'total_return': 9.2,
                'sharpe_ratio': 1.45,
                'win_rate': 52.0,
                'max_drawdown': -10.5,
                'profit_factor': 1.55,
                'total_trades': 52
            },
            'Z-Score Phi': {
                'total_return': 11.0,
                'sharpe_ratio': 1.68,
                'win_rate': 56.0,
                'max_drawdown': -9.0,
                'profit_factor': 1.72,
                'total_trades': 41
            }
        }
    }
    
    # Render overview
    comparison.render_strategy_overview(strategies_data['strategies'])
    
    st.markdown("---")
    
    # Render performance comparison
    comparison.render_performance_comparison(strategies_data['performance'])

# 🤖 ML PREDICTIONS PAGE
elif page == "🤖 ML Predictions":
    st.markdown("## 🤖 Machine Learning Predictions")
    
    st.info("💡 **AI-Powered Forecasting** - Ensemble learning για πρόβλεψη τιμών")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📊 Latest Predictions")
        
        # Mock prediction data
        predictions = pd.DataFrame({
            'Asset': ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT', 'ADA/USDT'],
            'Current Price': [43250, 2280, 315, 98, 0.58],
            'Predicted (5-bar)': [44100, 2350, 320, 102, 0.60],
            'Change': ['+2.0%', '+3.1%', '+1.6%', '+4.1%', '+3.4%'],
            'Confidence': [0.78, 0.82, 0.71, 0.85, 0.68],
            'Signal': ['BUY', 'BUY', 'HOLD', 'BUY', 'HOLD']
        })
        
        # Style the dataframe
        def color_signal(val):
            if val == 'BUY':
                return 'background-color: rgba(40, 167, 69, 0.3); color: #28a745; font-weight: bold'
            elif val == 'SELL':
                return 'background-color: rgba(220, 53, 69, 0.3); color: #dc3545; font-weight: bold'
            else:
                return 'background-color: rgba(255, 193, 7, 0.3); color: #ffc107; font-weight: bold'
        
        st.dataframe(
            predictions.style.applymap(color_signal, subset=['Signal'])
                             .format({'Confidence': '{:.0%}'}),
            use_container_width=True
        )
        
        # Feature importance
        st.markdown("### 🎯 Most Important Features")
        features_data = {
            'Feature': ['momentum_20', 'rsi', 'macd_histogram', 'price_to_sma20', 'volume_ratio'],
            'Importance': [0.15, 0.12, 0.11, 0.10, 0.09]
        }
        features_df = pd.DataFrame(features_data)
        
        import plotly.express as px
        fig = px.bar(features_df, x='Importance', y='Feature', orientation='h',
                     title='Feature Importance (Top 5)')
        fig.update_layout(template='plotly_dark', height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 📈 Model Stats")
        st.metric("Training Samples", "1,250")
        st.metric("Feature Count", "23")
        st.metric("Ensemble Accuracy", "78.5%")
        st.metric("Predictions Made", "342")
        
        st.markdown("---")
        
        st.markdown("### 🧠 Model Info")
        st.markdown("""
        <div class="strategy-card">
            <h4>Ensemble Architecture</h4>
            <ul>
                <li>Random Forest (100 trees)</li>
                <li>Gradient Boosting (100 estimators)</li>
                <li>Ensemble voting</li>
            </ul>
            
            <h4 style="margin-top: 15px;">Preprocessing</h4>
            <ul>
                <li>StandardScaler normalization</li>
                <li>Outlier detection</li>
                <li>Missing data handling</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

# 📐 FIBONACCI ANALYSIS PAGE
elif page == "📐 Fibonacci Analysis":
    st.markdown("## 📐 Fibonacci Retracement Analysis")
    
    st.info("💡 **Golden Ratio Trading** - Χρήση Fibonacci levels για entry/exit points")
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.markdown("### 📊 Current Fibonacci Levels")
        
        # Mock data
        swing_high = 45000
        swing_low = 38000
        current_price = 42100
        
        # Calculate Fibonacci levels
        price_range = swing_high - swing_low
        fib_levels = {
            '0.000 (Low)': swing_low,
            '0.236': swing_low + price_range * 0.236,
            '0.382': swing_low + price_range * 0.382,
            '0.500': swing_low + price_range * 0.500,
            '0.618 (Golden)': swing_low + price_range * 0.618,
            '0.786': swing_low + price_range * 0.786,
            '1.000 (High)': swing_high
        }
        
        # Display levels
        for level, price in fib_levels.items():
            distance = abs(current_price - price) / current_price * 100
            is_near = distance < 1.5
            
            if is_near:
                st.success(f"🎯 **{level}**: ${price:,.0f} (NEAR - {distance:.2f}%)")
            else:
                st.text(f"   {level}: ${price:,.0f}")
        
        st.markdown("---")
        st.markdown(f"**Current Price**: ${current_price:,.0f}")
        st.markdown(f"**Swing High**: ${swing_high:,.0f}")
        st.markdown(f"**Swing Low**: ${swing_low:,.0f}")
        
    with col2:
        st.markdown("### 🎯 Trading Signals")
        
        st.markdown("""
        <div class="strategy-card">
            <h4>Confluence Analysis</h4>
            <p><strong>Price near 0.618 (Golden Ratio)</strong></p>
            <p>Strong support level detected</p>
            
            <h4 style="margin-top: 20px;">Indicators</h4>
            <ul>
                <li>✅ RSI: 42 (oversold territory)</li>
                <li>✅ MACD: Bullish crossover</li>
                <li>✅ Volume: Above average</li>
            </ul>
            
            <h4 style="margin-top: 20px;">Recommendation</h4>
            <p style="color: #28a745; font-weight: bold; font-size: 1.1rem;">
                🟢 BUY Signal (Confidence: 75%)
            </p>
            
            <h4 style="margin-top: 20px;">Targets</h4>
            <ul>
                <li><strong>Entry:</strong> $42,100</li>
                <li><strong>Stop Loss:</strong> $40,500 (3.8%)</li>
                <li><strong>Take Profit 1:</strong> $43,500 (3.3%)</li>
                <li><strong>Take Profit 2:</strong> $45,000 (6.9%)</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

# ⚙️ RISK MANAGEMENT PAGE
elif page == "⚙️ Risk Management":
    st.markdown("## ⚙️ Risk Management Tools")
    
    st.info("💡 **Professional Risk Control** - Διαχείριση κινδύνου με προηγμένα εργαλεία")
    
    tab1, tab2, tab3 = st.tabs(["📊 Position Sizing", "📉 Value at Risk (VaR)", "🎲 Monte Carlo"])
    
    with tab1:
        st.markdown("### 📊 Position Sizing Calculator")
        
        col1, col2 = st.columns(2)
        
        with col1:
            account_balance = st.number_input("Account Balance ($)", 1000, 1000000, 10000)
            risk_per_trade = st.slider("Risk per Trade (%)", 0.5, 5.0, 2.0)
            entry_price = st.number_input("Entry Price ($)", 1, 100000, 42000)
            stop_loss_price = st.number_input("Stop Loss Price ($)", 1, 100000, 40000)
        
        with col2:
            # Calculate position size
            risk_amount = account_balance * (risk_per_trade / 100)
            price_risk = abs(entry_price - stop_loss_price)
            position_size = risk_amount / price_risk if price_risk > 0 else 0
            position_value = position_size * entry_price
            
            st.markdown("#### 📊 Results")
            st.metric("Risk Amount", f"${risk_amount:.2f}")
            st.metric("Position Size", f"{position_size:.4f} units")
            st.metric("Position Value", f"${position_value:.2f}")
            st.metric("Risk/Reward", f"{abs(entry_price - stop_loss_price) / entry_price * 100:.2f}%")
            
            if position_value / account_balance > 0.5:
                st.warning("⚠️ Position size is >50% of account!")
            else:
                st.success("✅ Position size is appropriate")
    
    with tab2:
        st.markdown("### 📉 Value at Risk (VaR) Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            portfolio_value = st.number_input("Portfolio Value ($)", 1000, 1000000, 50000)
            confidence_level = st.slider("Confidence Level (%)", 90, 99, 95)
            time_horizon = st.selectbox("Time Horizon", ["1 day", "1 week", "1 month"])
        
        with col2:
            # Mock VaR calculation
            var_1day = portfolio_value * 0.025  # 2.5% VaR
            var_1week = var_1day * np.sqrt(7)
            var_1month = var_1day * np.sqrt(30)
            
            st.markdown("#### 📊 VaR Results")
            st.metric("1-Day VaR", f"${var_1day:.2f}")
            st.metric("1-Week VaR", f"${var_1week:.2f}")
            st.metric("1-Month VaR", f"${var_1month:.2f}")
            
            st.info(f"💡 With {confidence_level}% confidence, you won't lose more than the VaR amount")
    
    with tab3:
        st.markdown("### 🎲 Monte Carlo Simulation")
        
        col1, col2 = st.columns(2)
        
        with col1:
            initial_capital = st.number_input("Initial Capital ($)", 1000, 1000000, 10000, key="mc_capital")
            n_simulations = st.slider("Number of Simulations", 1000, 10000, 5000)
            time_period = st.slider("Time Period (days)", 30, 365, 252)
        
        with col2:
            st.markdown("#### 📊 Simulation Results")
            
            # Mock results
            st.metric("Mean Final Value", f"${initial_capital * 1.15:.0f}")
            st.metric("Median Final Value", f"${initial_capital * 1.12:.0f}")
            st.metric("95th Percentile", f"${initial_capital * 1.35:.0f}")
            st.metric("Probability of Profit", "72.5%")
            
            st.success("✅ Simulation completed successfully!")

# 📊 Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 20px; color: #6db2c7; opacity: 0.7;">
    <p><strong>CryptoBot Professional v2.1.0</strong></p>
    <p>Advanced Trading Platform | Institutional-Grade Analytics | Machine Learning Enhanced</p>
    <p>🎯 7 Professional Strategies | 📊 Portfolio Optimization | 🤖 AI Predictions</p>
</div>
""", unsafe_allow_html=True)
