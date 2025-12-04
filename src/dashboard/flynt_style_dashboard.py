# flynt_style_dashboard.py - FLYNT-Inspired Professional Dashboard με Advanced Features
import streamlit as st
import pandas as pd
import numpy as np
import requests
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import time
import json
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import advanced modules
try:
    from strategies import (
        AdvancedFibonacciStrategy,
        MLMomentumStrategy,
        RSIEMAATRStrategy,
        ZScorePhiStrategy
    )
    from utils.portfolio_optimizer import PortfolioOptimizer
    from dashboard.strategy_comparison_dashboard import StrategyComparisonDashboard
    ADVANCED_FEATURES_AVAILABLE = True
except ImportError as e:
    ADVANCED_FEATURES_AVAILABLE = False
    print(f"Advanced features not available: {e}")

# 🎨 Page Configuration - FLYNT Style
st.set_page_config(
    page_title="CryptoBot",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.flynt.gr',
        'Report a bug': None,
        'About': "# CryptoBot Pro\nFLYNT-Inspired Professional Trading Dashboard"
    }
)

# 🎨 FLYNT-Inspired CSS Styling
st.markdown("""
<style>
    /* Import FLYNT Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@100;200;300;400;500;600;700;800;900&family=Arimo:wght@400;700&family=DM+Sans:wght@300;400;500;600;700&display=swap');
    
    /* FLYNT Color Variables */
    :root {
        --flynt-primary: #187794;
        --flynt-secondary: #ffffff;
        --flynt-tertiary: #181818;
        --flynt-button-idle: #6db2c7;
        --flynt-button-hover: #303030;
        --flynt-content: #d0d0d0;
        --flynt-background: #0f1419;
        --flynt-card-bg: rgba(255, 255, 255, 0.05);
        --flynt-border: rgba(109, 178, 199, 0.2);
        --flynt-accent: #4a9eff;
        --flynt-success: #28a745;
        --flynt-danger: #dc3545;
        --flynt-warning: #ffc107;
    }
    
    /* Global Styling */
    .stApp {
        background: linear-gradient(135deg, var(--flynt-background) 0%, var(--flynt-tertiary) 100%);
        font-family: 'Inter', sans-serif;
        color: var(--flynt-content);
    }
    
    .main > div {
        padding: 0 !important;
        max-width: 1200px !important;
        margin: 0 auto !important;
    }
    
    /* Hide Streamlit Branding */
    .stDeployButton, #MainMenu, footer {
        visibility: hidden;
    }
    
    /* Force sidebar visibility */
    [data-testid="stSidebar"][aria-expanded="true"] {
        transform: none !important;
        visibility: visible !important;
    }
    
    .stSidebar {
        visibility: visible !important;
        display: block !important;
    }
    
    /* Sidebar toggle button */
    [data-testid="collapsedControl"] {
        color: var(--flynt-secondary) !important;
        background: var(--flynt-primary) !important;
        border-radius: 4px !important;
    }
    
    /* FLYNT Header */
    .flynt-header {
        text-align: center;
        padding: 40px 0 30px 0;
        background: linear-gradient(135deg, var(--flynt-primary), var(--flynt-button-idle));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-family: 'Arimo', sans-serif;
        font-size: 3.25rem;
        font-weight: 700;
        line-height: 1.2;
        letter-spacing: -1px;
        margin-bottom: 20px;
    }
    
    .flynt-subtitle {
        text-align: center;
        color: var(--flynt-content);
        font-family: 'Inter', sans-serif;
        font-size: 1.125rem;
        font-weight: 300;
        margin-bottom: 40px;
        opacity: 0.8;
    }
    
    /* FLYNT Cards */
    .flynt-card {
        background: var(--flynt-card-bg);
        backdrop-filter: blur(10px);
        border: 1px solid var(--flynt-border);
        border-radius: 16px;
        padding: 24px;
        margin: 16px 0;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .flynt-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, var(--flynt-primary), var(--flynt-button-idle));
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .flynt-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 32px rgba(24, 119, 148, 0.15);
        border-color: var(--flynt-button-idle);
    }
    
    .flynt-card:hover::before {
        opacity: 1;
    }
    
    /* FLYNT Metrics */
    .flynt-metric {
        background: var(--flynt-card-bg);
        border: 1px solid var(--flynt-border);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .flynt-metric:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 24px rgba(24, 119, 148, 0.2);
        border-color: var(--flynt-primary);
    }
    
    .metric-value {
        font-family: 'Arimo', sans-serif;
        font-size: 2.5rem;
        font-weight: 700;
        color: var(--flynt-primary);
        text-shadow: 0 0 15px rgba(24, 119, 148, 0.3);
        margin-bottom: 8px;
        display: block;
    }
    
    .metric-label {
        font-family: 'Inter', sans-serif;
        font-size: 0.875rem;
        font-weight: 500;
        color: var(--flynt-content);
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 4px;
    }
    
    .metric-change {
        font-family: 'DM Sans', sans-serif;
        font-size: 0.8rem;
        font-weight: 500;
    }
    
    .positive { color: var(--flynt-success); }
    .negative { color: var(--flynt-danger); }
    .neutral { color: var(--flynt-warning); }
    
    /* FLYNT Section Headers */
    .flynt-section {
        font-family: 'Arimo', sans-serif;
        font-size: 1.875rem;
        font-weight: 700;
        color: var(--flynt-secondary);
        margin: 32px 0 20px 0;
        position: relative;
        padding-left: 20px;
    }
    
    .flynt-section::before {
        content: '';
        position: absolute;
        left: 0;
        top: 50%;
        transform: translateY(-50%);
        width: 4px;
        height: 30px;
        background: linear-gradient(180deg, var(--flynt-primary), var(--flynt-button-idle));
        border-radius: 2px;
    }
    
    /* FLYNT Sidebar - Updated selectors */
    .stSidebar {
        background: linear-gradient(180deg, var(--flynt-tertiary), var(--flynt-background)) !important;
        border-right: 1px solid var(--flynt-border) !important;
    }
    
    .stSidebar .stMarkdown h2,
    .stSidebar .stMarkdown h3,
    .stSidebar .stMarkdown h4 {
        color: var(--flynt-secondary) !important;
        font-family: 'Arimo', sans-serif !important;
        font-weight: 700 !important;
    }
    
    .stSidebar .stMarkdown p {
        color: var(--flynt-content) !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Sidebar content */
    .css-1d391kg, [data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--flynt-tertiary), var(--flynt-background)) !important;
        border-right: 1px solid var(--flynt-border) !important;
    }
    
    [data-testid="stSidebar"] > div {
        background: transparent !important;
    }
    
    /* FLYNT Buttons */
    .stButton > button {
        background: var(--flynt-button-idle);
        color: var(--flynt-secondary);
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        font-family: 'DM Sans', sans-serif;
        font-weight: 600;
        font-size: 14px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .stButton > button:hover {
        background: var(--flynt-button-hover);
        transform: translateY(-1px);
        box-shadow: 0 4px 15px rgba(109, 178, 199, 0.3);
    }
    
    /* FLYNT Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: var(--flynt-card-bg);
        padding: 6px;
        border-radius: 12px;
        border: 1px solid var(--flynt-border);
        justify-content: center;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        color: var(--flynt-content);
        font-family: 'DM Sans', sans-serif;
        font-weight: 500;
        font-size: 14px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        padding: 12px 20px;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: var(--flynt-primary);
        color: var(--flynt-secondary);
        box-shadow: 0 2px 8px rgba(24, 119, 148, 0.3);
    }
    
    /* FLYNT Status Indicators */
    .status-online {
        display: inline-block;
        width: 10px;
        height: 10px;
        background: var(--flynt-success);
        border-radius: 50%;
        margin-right: 8px;
        animation: pulse-online 2s infinite;
    }
    
    .status-offline {
        display: inline-block;
        width: 10px;
        height: 10px;
        background: var(--flynt-danger);
        border-radius: 50%;
        margin-right: 8px;
    }
    
    @keyframes pulse-online {
        0% { 
            box-shadow: 0 0 0 0 rgba(40, 167, 69, 0.7); 
        }
        70% { 
            box-shadow: 0 0 0 6px rgba(40, 167, 69, 0); 
        }
        100% { 
            box-shadow: 0 0 0 0 rgba(40, 167, 69, 0); 
        }
    }
    
    /* FLYNT Data Tables */
    .stDataFrame {
        background: var(--flynt-card-bg);
        border-radius: 12px;
        border: 1px solid var(--flynt-border);
        overflow: hidden;
    }
    
    .stDataFrame table {
        font-family: 'Inter', sans-serif;
        font-size: 0.875rem;
    }
    
    .stDataFrame th {
        background: var(--flynt-primary);
        color: var(--flynt-secondary);
        font-family: 'DM Sans', sans-serif;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* FLYNT Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--flynt-tertiary);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--flynt-primary);
        border-radius: 4px;
        transition: background 0.3s ease;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--flynt-button-idle);
    }
    
    /* FLYNT Responsive */
    @media (max-width: 768px) {
        .flynt-header {
            font-size: 2.5rem;
            padding: 30px 0 20px 0;
        }
        
        .flynt-section {
            font-size: 1.5rem;
            margin: 24px 0 16px 0;
        }
        
        .metric-value {
            font-size: 2rem;
        }
    }
    
    /* FLYNT Animations */
    .flynt-fade-in {
        animation: fadeIn 0.6s ease-out;
    }
    
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
</style>
""", unsafe_allow_html=True)

# 🚀 FLYNT Header - Professional
st.markdown("""
<div class="flynt-fade-in">
    <div style="display: flex; align-items: center; justify-content: center; margin-bottom: 20px;">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" style="margin-right: 16px;">
            <path d="M12 2L2 7L12 12L22 7L12 2Z" fill="#187794"/>
            <path d="M2 17L12 22L22 17" stroke="#6DB2C7" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M2 12L12 17L22 12" stroke="#6DB2C7" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        <h1 class="flynt-header" style="margin: 0;">CryptoBot Professional</h1>
    </div>
    <p class="flynt-subtitle">Advanced Cryptocurrency Trading Platform | Institutional-Grade Analytics</p>
</div>
""", unsafe_allow_html=True)

# 🎛️ FLYNT Sidebar - Professional
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; margin-bottom: 20px;">
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none">
            <circle cx="12" cy="12" r="10" stroke="#187794" stroke-width="2"/>
            <path d="M8 12L11 15L16 9" stroke="#6DB2C7" stroke-width="2" stroke-linecap="round"/>
        </svg>
        <h2 style="color: var(--flynt-secondary); font-family: 'Arimo', sans-serif; font-weight: 700; margin: 8px 0 0 0; font-size: 1.25rem;">Control Center</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # System Status Card - Professional
    st.markdown("""
    <div class="flynt-card">
        <div style="display: flex; align-items: center; margin-bottom: 16px;">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" style="margin-right: 8px;">
                <rect x="3" y="4" width="18" height="18" rx="2" ry="2" stroke="#187794" stroke-width="2"/>
                <line x1="16" y1="2" x2="16" y2="6" stroke="#187794" stroke-width="2"/>
                <line x1="8" y1="2" x2="8" y2="6" stroke="#187794" stroke-width="2"/>
                <line x1="3" y1="10" x2="21" y2="10" stroke="#187794" stroke-width="2"/>
            </svg>
            <h3 style="color: var(--flynt-secondary); font-family: 'Arimo', sans-serif; font-weight: 700; margin: 0; font-size: 1.1rem;">System Status</h3>
        </div>
        <div style="display: flex; align-items: center; margin: 12px 0;">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="#28a745" style="margin-right: 10px;">
                <circle cx="12" cy="12" r="10"/>
            </svg>
            <span style="font-family: 'Inter', sans-serif; font-size: 0.9rem;">Platform Online</span>
        </div>
        <div style="display: flex; align-items: center; margin: 12px 0;">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="#28a745" style="margin-right: 10px;">
                <circle cx="12" cy="12" r="10"/>
            </svg>
            <span style="font-family: 'Inter', sans-serif; font-size: 0.9rem;">Market Data Connected</span>
        </div>
        <div style="display: flex; align-items: center; margin: 12px 0;">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="#28a745" style="margin-right: 10px;">
                <circle cx="12" cy="12" r="10"/>
            </svg>
            <span style="font-family: 'Inter', sans-serif; font-size: 0.9rem;">API Services Active</span>
        </div>
        <div style="display: flex; align-items: center; margin: 12px 0;">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="#dc3545" style="margin-right: 10px;">
                <circle cx="12" cy="12" r="10"/>
            </svg>
            <span style="font-family: 'Inter', sans-serif; font-size: 0.9rem;">Trading Bots Standby</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick Actions - Professional
    st.markdown("""
    <div style="display: flex; align-items: center; margin: 20px 0 12px 0;">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" style="margin-right: 8px;">
            <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" stroke="#6DB2C7" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        <h3 style="color: var(--flynt-secondary); font-family: 'Arimo', sans-serif; font-weight: 700; margin: 0; font-size: 1rem;">Quick Actions</h3>
    </div>
    """, unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("↻ Refresh", key="refresh", use_container_width=True):
            st.rerun()
    with col2:
        if st.button("▶ Start Bot", key="start", use_container_width=True):
            st.success("Bot initializing...")
    
    # Advanced Features Link - NEW
    st.markdown("---")
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(24,119,148,0.2), rgba(109,178,199,0.1)); 
                border: 2px solid #187794; border-radius: 8px; padding: 15px; margin: 10px 0;">
        <h4 style="color: #6db2c7; margin: 0 0 10px 0; text-align: center;">🎯 Advanced Features</h4>
        <p style="font-size: 0.85rem; text-align: center; margin: 0;">
            ✨ ML Strategies<br/>
            📐 Fibonacci Analysis<br/>
            📊 Portfolio Optimizer<br/>
            📈 Strategy Comparison
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚀 Launch Advanced Dashboard", key="advanced", use_container_width=True, type="primary"):
        st.info("💡 **Tip**: Run `streamlit run src/dashboard/advanced_dashboard.py` to access advanced features!")
    
    # Settings Panel - Professional
    st.markdown("""
    <div style="display: flex; align-items: center; margin: 20px 0 12px 0;">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" style="margin-right: 8px;">
            <circle cx="12" cy="12" r="3" stroke="#6DB2C7" stroke-width="2"/>
            <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82L20.94 18a2 2 0 0 1 0 2.83L19.17 22.6a2 2 0 0 1-2.83 0l-1.15-1.15a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V24a2 2 0 0 1-2 2H8.5a2 2 0 0 1-2-2v-1.47a1.65 1.65 0 0 0-1-1.51 1.65 1.65 0 0 0-1.82.33L2.4 22.6a2 2 0 0 1-2.83 0L-1.6 20.83a2 2 0 0 1 0-2.83L-.45 16.85a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H-3a2 2 0 0 1-2-2V9.5a2 2 0 0 1 2-2h1.47a1.65 1.65 0 0 0 1.51-1 1.65 1.65 0 0 0-.33-1.82L-3.6 3.4a2 2 0 0 1 0-2.83L-1.83.6a2 2 0 0 1 2.83 0l1.15 1.15a1.65 1.65 0 0 0 1.82.33H4a1.65 1.65 0 0 0 1-1.51V0a2 2 0 0 1 2-2h2.5a2 2 0 0 1 2 2v1.47a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33L15.57.6a2 2 0 0 1 2.83 0L20.4 2.4a2 2 0 0 1 0 2.83l-1.15 1.15a1.65 1.65 0 0 0-.33 1.82v.5a1.65 1.65 0 0 0 1.51 1H22a2 2 0 0 1 2 2v2.5a2 2 0 0 1-2 2h-1.47a1.65 1.65 0 0 0-1.51 1z" stroke="#6DB2C7" stroke-width="2"/>
        </svg>
        <h3 style="color: var(--flynt-secondary); font-family: 'Arimo', sans-serif; font-weight: 700; margin: 0; font-size: 1rem;">Configuration</h3>
    </div>
    """, unsafe_allow_html=True)
    auto_refresh = st.toggle("🔄 Auto Refresh", value=True)
    demo_mode = st.toggle("🧪 Demo Mode", value=True)
    notifications = st.toggle("🔔 Notifications", value=True)
    
    if auto_refresh:
        refresh_rate = st.slider("Refresh Interval (sec)", 10, 300, 60)

# 📊 Data Fetching Functions
@st.cache_data(ttl=60)
def fetch_crypto_data():
    """Fetch live cryptocurrency data with FLYNT styling"""
    try:
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {
            'vs_currency': 'usd',
            'order': 'market_cap_desc',
            'per_page': 15,
            'page': 1,
            'sparkline': False,
            'price_change_percentage': '24h'
        }
        
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            return pd.DataFrame(response.json())
        else:
            return create_mock_data()
    except:
        return create_mock_data()

def create_mock_data():
    """Create mock data with FLYNT theme"""
    symbols = ['Bitcoin', 'Ethereum', 'Binance Coin', 'Cardano', 'Solana', 'Polkadot', 'Avalanche']
    data = []
    for symbol in symbols:
        data.append({
            'name': symbol,
            'symbol': symbol[:3].upper(),
            'current_price': np.random.uniform(1, 50000),
            'price_change_percentage_24h': np.random.uniform(-15, 15),
            'market_cap': np.random.uniform(1e9, 1e12),
            'total_volume': np.random.uniform(1e8, 1e11)
        })
    return pd.DataFrame(data)

# 📈 Fetch Market Data
with st.spinner("Fetching live market data..."):
    crypto_df = fetch_crypto_data()

# Market Overview Header - Professional with Real Crypto Icons
st.markdown("""
<div style="display: flex; align-items: center; margin: 30px 0 15px 0;">
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" style="margin-right: 10px;">
        <path d="M3 6h18l-1.5 9H4.5L3 6z" stroke="#6DB2C7" stroke-width="2" fill="none"/>
        <path d="M8 13v3M12 10v6M16 8v8" stroke="#6DB2C7" stroke-width="2"/>
        <circle cx="8" cy="16" r="1" fill="#6DB2C7"/>
        <circle cx="12" cy="16" r="1" fill="#6DB2C7"/>
        <circle cx="16" cy="16" r="1" fill="#6DB2C7"/>
    </svg>
    <h2 style="color: var(--flynt-primary); font-family: 'Arimo', sans-serif; font-weight: 700; margin: 0; font-size: 1.4rem;">Live Market Data</h2>
</div>
""", unsafe_allow_html=True)

# Real cryptocurrency logos definitions
crypto_icons = {
    'BTC': '''<svg width="20" height="20" viewBox="0 0 24 24" style="margin-right: 8px;">
        <circle cx="12" cy="12" r="12" fill="#F7931A"/>
        <path d="M12.3 7.2c-.8-.1-1.6.3-1.8 1.1l-.4 1.6c-.1.4.1.8.5.9l.5.1c.4.1.8-.1.9-.5l.4-1.6c.1-.8-.5-1.5-1.1-1.6zm2.4 3.2c.8-.2 1.3-.9 1.1-1.7-.2-.8-.9-1.3-1.7-1.1l-.3.1-.3-1.1c-.1-.4-.5-.6-.9-.5l-.9.2c-.4.1-.6.5-.5.9l.3 1.1-1.1.3-.3-1.1c-.1-.4-.5-.6-.9-.5l-.9.2c-.4.1-.6.5-.5.9l.3 1.1L7.5 9c-.4.1-.6.5-.5.9l.2.9c.1.4.5.6.9.5l.5-.1.9 3.5-.5.1c-.4.1-.6.5-.5.9l.2.9c.1.4.5.6.9.5l1.5-.4.3 1.1c.1.4.5.6.9.5l.9-.2c.4-.1.6-.5.5-.9l-.3-1.1 1.1-.3.3 1.1c.1.4.5.6.9.5l.9-.2c.4-.1.6-.5.5-.9l-.3-1.1.6-.2c.8-.2 1.3-.9 1.1-1.7-.2-.8-.9-1.3-1.7-1.1z" fill="white"/>
    </svg>''',
    'ETH': '''<svg width="20" height="20" viewBox="0 0 24 24" style="margin-right: 8px;">
        <circle cx="12" cy="12" r="12" fill="#627EEA"/>
        <path d="M12 3L7.5 12.5L12 15.5L16.5 12.5L12 3Z" fill="white" opacity="0.8"/>
        <path d="M7.5 13.5L12 21L16.5 13.5L12 16.5L7.5 13.5Z" fill="white" opacity="0.6"/>
    </svg>''',
    'BNB': '''<svg width="20" height="20" viewBox="0 0 24 24" style="margin-right: 8px;">
        <circle cx="12" cy="12" r="12" fill="#F3BA2F"/>
        <path d="M8.5 9.5L12 6L15.5 9.5L17.5 7.5L12 2L6.5 7.5L8.5 9.5Z" fill="white"/>
        <path d="M8.5 14.5L12 18L15.5 14.5L17.5 16.5L12 22L6.5 16.5L8.5 14.5Z" fill="white"/>
        <path d="M9.5 12L12 9.5L14.5 12L12 14.5L9.5 12Z" fill="white"/>
    </svg>'''
}

col1, col2, col3, col4 = st.columns(4)

with col1:
    btc_price = crypto_df.iloc[0]['current_price'] if not crypto_df.empty else 45123
    btc_change = crypto_df.iloc[0]['price_change_percentage_24h'] if not crypto_df.empty else 3.24
    change_class = "positive" if btc_change > 0 else "negative"
    
    st.markdown(f"""
    <div class="flynt-metric flynt-fade-in">
        <div style="display: flex; align-items: center; margin-bottom: 8px;">
            {crypto_icons['BTC']}
            <span class="metric-value">${btc_price:,.0f}</span>
        </div>
        <div class="metric-label">Bitcoin</div>
        <div class="metric-change {change_class}">
            {'↗' if btc_change > 0 else '↘'} {btc_change:+.2f}%
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    eth_price = crypto_df.iloc[1]['current_price'] if len(crypto_df) > 1 else 2834
    eth_change = crypto_df.iloc[1]['price_change_percentage_24h'] if len(crypto_df) > 1 else 1.8
    change_class = "positive" if eth_change > 0 else "negative"
    st.markdown(f"""
    <div class="flynt-metric flynt-fade-in">
        <div style="display: flex; align-items: center; margin-bottom: 8px;">
            {crypto_icons['ETH']}
            <span class="metric-value">${eth_price:,.0f}</span>
        </div>
        <div class="metric-label">Ethereum</div>
        <div class="metric-change {change_class}">{'↗' if eth_change > 0 else '↘'} {eth_change:+.2f}%</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    bnb_price = crypto_df.iloc[2]['current_price'] if len(crypto_df) > 2 else 652
    bnb_change = crypto_df.iloc[2]['price_change_percentage_24h'] if len(crypto_df) > 2 else 0.3
    change_class = "positive" if bnb_change > 0 else "negative"
    st.markdown(f"""
    <div class="flynt-metric flynt-fade-in">
        <div style="display: flex; align-items: center; margin-bottom: 8px;">
            {crypto_icons['BNB']}
            <span class="metric-value">${bnb_price:,.0f}</span>
        </div>
        <div class="metric-label">BNB</div>
        <div class="metric-change {change_class}">{'↗' if bnb_change > 0 else '↘'} {bnb_change:+.2f}%</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    total_cap = crypto_df['market_cap'].sum() / 1e12 if not crypto_df.empty else 2.89
    st.markdown(f"""
    <div class="flynt-metric flynt-fade-in">
        <div style="display: flex; align-items: center; margin-bottom: 8px;">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" style="margin-right: 8px;">
                <circle cx="12" cy="12" r="10" stroke="#6DB2C7" stroke-width="2"/>
                <path d="M8 12l2 2 6-6" stroke="#6DB2C7" stroke-width="2"/>
            </svg>
            <span class="metric-value">${total_cap:.2f}T</span>
        </div>
        <div class="metric-label">Total Market Cap</div>
        <div class="metric-change positive">↗ +2.1%</div>
    </div>
    """, unsafe_allow_html=True)

# 📋 FLYNT Main Tabs με Advanced Features
if ADVANCED_FEATURES_AVAILABLE:
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
        "🏠 Dashboard", 
        "📊 Markets", 
        "🤖 Trading Bots", 
        "🎯 Advanced Strategies",
        "📈 Portfolio Optimizer",
        "📉 Strategy Comparison",
        "🤖 ML Predictions",
        "⚙️ Configuration"
    ])
else:
    tab1, tab2, tab3, tab4 = st.tabs([
        "🏠 Dashboard", 
        "📊 Markets", 
        "🤖 Trading Bots", 
        "⚙️ Configuration"
    ])


with tab1:
    st.markdown('<h2 class="flynt-section">🎯 Portfolio Performance</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2.5, 1])
    
    with col1:
        # FLYNT Portfolio Chart
        fig = go.Figure()
        
        dates = pd.date_range(start='2025-01-01', end='2025-08-12', freq='D')
        portfolio_value = 25000 * (1 + np.cumsum(np.random.randn(len(dates)) * 0.008))
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=portfolio_value,
            mode='lines',
            name='Portfolio Value',
            line=dict(color='#187794', width=3),
            fill='tonexty',
            fillcolor='rgba(24, 119, 148, 0.1)'
        ))
        
        fig.update_layout(
            title={
                'text': '📈 Portfolio Growth Trajectory',
                'font': {'size': 20, 'color': '#ffffff', 'family': 'Arimo'}
            },
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font={'color': '#d0d0d0', 'family': 'Inter'},
            xaxis=dict(gridcolor='rgba(109,178,199,0.2)', showgrid=True),
            yaxis=dict(gridcolor='rgba(109,178,199,0.2)', showgrid=True),
            height=400,
            margin=dict(t=50, b=50, l=50, r=50)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("""
        <div class="flynt-card">
            <h3 style="color: var(--flynt-secondary); font-family: 'Arimo', sans-serif; font-weight: 700; margin-bottom: 16px;">💰 Portfolio Stats</h3>
            <div style="margin: 12px 0;">
                <strong>Total Value:</strong><br>
                <span style="font-size: 1.5rem; color: var(--flynt-primary); font-family: 'Arimo', sans-serif; font-weight: 700;">$52,847</span>
            </div>
            <div style="margin: 12px 0;">
                <strong>Today's P&L:</strong><br>
                <span class="positive" style="font-size: 1.2rem; font-weight: 600;">+$1,394 (+2.7%)</span>
            </div>
            <div style="margin: 12px 0;">
                <strong>Best Performer:</strong><br>
                <span style="color: var(--flynt-button-idle);">BTC (+4.8%)</span>
            </div>
            <div style="margin: 12px 0;">
                <strong>Active Positions:</strong> 7
            </div>
            <div style="margin: 12px 0;">
                <strong>Success Rate:</strong> 76.3%
            </div>
            <div style="margin: 12px 0;">
                <strong>Sharpe Ratio:</strong> 1.84
            </div>
        </div>
        """, unsafe_allow_html=True)

with tab2:
    # Trading Analysis Header - Professional
    st.markdown("""
    <div style="display: flex; align-items: center; margin: 30px 0 15px 0;">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" style="margin-right: 10px;">
            <path d="M3 3v18h18" stroke="#6DB2C7" stroke-width="2"/>
            <path d="M7 16L12 8L16 12L21 4" stroke="#6DB2C7" stroke-width="2" stroke-linecap="round"/>
            <circle cx="7" cy="16" r="1.5" fill="#6DB2C7"/>
            <circle cx="12" cy="8" r="1.5" fill="#6DB2C7"/>
            <circle cx="16" cy="12" r="1.5" fill="#6DB2C7"/>
            <circle cx="21" cy="4" r="1.5" fill="#6DB2C7"/>
        </svg>
        <h2 style="color: var(--flynt-primary); font-family: 'Arimo', sans-serif; font-weight: 700; margin: 0; font-size: 1.4rem;">Live Market Analysis</h2>
    </div>
    """, unsafe_allow_html=True)
    
    if not crypto_df.empty:
        # Format data for FLYNT table
        display_df = crypto_df[['name', 'symbol', 'current_price', 'price_change_percentage_24h', 'market_cap']].copy()
        display_df.columns = ['Cryptocurrency', 'Symbol', 'Price (USD)', '24h Change (%)', 'Market Cap (USD)']
        display_df['Price (USD)'] = display_df['Price (USD)'].apply(lambda x: f"${x:,.2f}")
        display_df['24h Change (%)'] = display_df['24h Change (%)'].apply(lambda x: f"{x:+.2f}%")
        display_df['Market Cap (USD)'] = display_df['Market Cap (USD)'].apply(lambda x: f"${x:,.0f}")
        
        st.dataframe(display_df, use_container_width=True, height=600)
    else:
        st.error("❌ Unable to fetch live market data")

with tab3:
    # Trading Bot Fleet Header - Professional
    st.markdown("""
    <div style="display: flex; align-items: center; margin: 30px 0 15px 0;">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" style="margin-right: 10px;">
            <rect x="3" y="3" width="18" height="18" rx="4" stroke="#6DB2C7" stroke-width="2"/>
            <circle cx="9" cy="9" r="2" stroke="#6DB2C7" stroke-width="1.5"/>
            <circle cx="15" cy="15" r="2" stroke="#6DB2C7" stroke-width="1.5"/>
            <path d="M12 12h3M9 12H6" stroke="#6DB2C7" stroke-width="1.5"/>
            <path d="M12 9v6" stroke="#6DB2C7" stroke-width="1.5"/>
        </svg>
        <h2 style="color: var(--flynt-primary); font-family: 'Arimo', sans-serif; font-weight: 700; margin: 0; font-size: 1.4rem;">Trading Bot Fleet</h2>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="flynt-card">
            <div style="display: flex; align-items: center; margin-bottom: 12px;">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" style="margin-right: 8px;">
                    <path d="M12 2L2 7v10c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V7l-10-5z" stroke="#6DB2C7" stroke-width="2" fill="none"/>
                    <path d="M12 12v9M7 9v8M17 9v8" stroke="#6DB2C7" stroke-width="1.5"/>
                </svg>
                <h4 style="color: var(--flynt-secondary); font-family: 'Arimo', sans-serif; margin: 0;">RSI Momentum Bot</h4>
            </div>
            <p><span class="status-online"></span><strong>Status:</strong> Active</p>
            <p><strong>Pair:</strong> BTC/USDT</p>
            <p><strong>Strategy:</strong> RSI + EMA + ATR</p>
            <p><strong>Profit:</strong> <span class="positive">+$3,247</span></p>
            <p><strong>Trades:</strong> 67 (51 wins)</p>
            <p><strong>Uptime:</strong> 24h 17m</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="flynt-card">
            <div style="display: flex; align-items: center; margin-bottom: 12px;">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" style="margin-right: 8px;">
                    <circle cx="12" cy="12" r="12" fill="#627EEA"/>
                    <path d="M12 3L7.5 12.5L12 15.5L16.5 12.5L12 3Z" fill="white" opacity="0.8"/>
                    <path d="M7.5 13.5L12 21L16.5 13.5L12 16.5L7.5 13.5Z" fill="white" opacity="0.6"/>
                </svg>
                <h4 style="color: var(--flynt-secondary); font-family: 'Arimo', sans-serif; margin: 0;">EMA Crossover Bot</h4>
            </div>
            <p><span class="status-online"></span><strong>Status:</strong> Active</p>
            <p><strong>Pair:</strong> ETH/USDT</p>
            <p><strong>Strategy:</strong> EMA 12/26 Cross</p>
            <p><strong>Profit:</strong> <span class="positive">+$2,156</span></p>
            <p><strong>Trades:</strong> 43 (32 wins)</p>
            <p><strong>Uptime:</strong> 18h 52m</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="flynt-card">
            <div style="display: flex; align-items: center; margin-bottom: 12px;">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" style="margin-right: 8px;">
                    <rect x="3" y="3" width="7" height="7" rx="1" stroke="#6DB2C7" stroke-width="1.5"/>
                    <rect x="14" y="3" width="7" height="7" rx="1" stroke="#6DB2C7" stroke-width="1.5"/>
                    <rect x="3" y="14" width="7" height="7" rx="1" stroke="#6DB2C7" stroke-width="1.5"/>
                    <rect x="14" y="14" width="7" height="7" rx="1" stroke="#6DB2C7" stroke-width="1.5"/>
                    <circle cx="6.5" cy="6.5" r="1" fill="#6DB2C7"/>
                    <circle cx="17.5" cy="6.5" r="1" fill="#6DB2C7"/>
                    <circle cx="6.5" cy="17.5" r="1" fill="#6DB2C7"/>
                    <circle cx="17.5" cy="17.5" r="1" fill="#6DB2C7"/>
                </svg>
                <h4 style="color: var(--flynt-secondary); font-family: 'Arimo', sans-serif; margin: 0;">Grid Trading Bot</h4>
            </div>
            <p><span class="status-offline"></span><strong>Status:</strong> Paused</p>
            <p><strong>Pair:</strong> ADA/USDT</p>
            <p><strong>Strategy:</strong> Grid Range</p>
            <p><strong>Profit:</strong> <span class="negative">-$89</span></p>
            <p><strong>Trades:</strong> 234 (178 wins)</p>
            <p><strong>Uptime:</strong> Stopped</p>
        </div>
        """, unsafe_allow_html=True)

with tab4:
    # System Configuration Header - Professional
    st.markdown("""
    <div style="display: flex; align-items: center; margin: 30px 0 15px 0;">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" style="margin-right: 10px;">
            <circle cx="12" cy="12" r="3" stroke="#6DB2C7" stroke-width="2"/>
            <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82L20.94 18a2 2 0 0 1 0 2.83L19.17 22.6a2 2 0 0 1-2.83 0l-1.15-1.15a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V24a2 2 0 0 1-2 2H8.5a2 2 0 0 1-2-2v-1.47a1.65 1.65 0 0 0-1-1.51 1.65 1.65 0 0 0-1.82.33L2.4 22.6a2 2 0 0 1-2.83 0L-1.6 20.83a2 2 0 0 1 0-2.83L-.45 16.85a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H-3a2 2 0 0 1-2-2V9.5a2 2 0 0 1 2-2h1.47a1.65 1.65 0 0 0 1.51-1 1.65 1.65 0 0 0-.33-1.82L-3.6 3.4a2 2 0 0 1 0-2.83L-1.83.6a2 2 0 0 1 2.83 0l1.15 1.15a1.65 1.65 0 0 0 1.82.33H4a1.65 1.65 0 0 0 1-1.51V0a2 2 0 0 1 2-2h2.5a2 2 0 0 1 2 2v1.47a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33L15.57.6a2 2 0 0 1 2.83 0L20.4 2.4a2 2 0 0 1 0 2.83l-1.15 1.15a1.65 1.65 0 0 0-.33 1.82v.5a1.65 1.65 0 0 0 1.51 1H22a2 2 0 0 1 2 2v2.5a2 2 0 0 1-2 2h-1.47a1.65 1.65 0 0 0-1.51 1z" stroke="#6DB2C7" stroke-width="2"/>
        </svg>
        <h2 style="color: var(--flynt-primary); font-family: 'Arimo', sans-serif; font-weight: 700; margin: 0; font-size: 1.4rem;">System Configuration</h2>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="flynt-card">
            <h3 style="color: var(--flynt-secondary); font-family: 'Arimo', sans-serif; margin-bottom: 16px;">🔧 Trading Parameters</h3>
        </div>
        """, unsafe_allow_html=True)
        
        st.number_input("Maximum Position Size (%)", min_value=1, max_value=50, value=15, key="pos_size")
        st.number_input("Stop Loss Percentage (%)", min_value=0.5, max_value=10.0, value=2.5, step=0.1, key="stop_loss")
        st.number_input("Take Profit Percentage (%)", min_value=1.0, max_value=25.0, value=6.0, step=0.5, key="take_profit")
        st.selectbox("Trading Mode", ["Demo Trading", "Live Trading"], index=0, key="mode")
    
    with col2:
        st.markdown("""
        <div class="flynt-card">
            <h3 style="color: var(--flynt-secondary); font-family: 'Arimo', sans-serif; margin-bottom: 16px;">🔒 API Configuration</h3>
        </div>
        """, unsafe_allow_html=True)
        
        st.text_input("Binance API Key", type="password", placeholder="Enter your Binance API key", key="api_key")
        st.text_input("Binance Secret Key", type="password", placeholder="Enter your secret key", key="secret_key")
        st.checkbox("Enable Testnet Mode", value=True, key="testnet")
        st.checkbox("Enable Push Notifications", value=notifications, key="push_notif")

# 🎯 Advanced Strategy Tab
if ADVANCED_FEATURES_AVAILABLE:
    with tab5:
        st.markdown('<h2 class="flynt-section">🎯 Advanced Trading Strategies</h2>', unsafe_allow_html=True)
        
        st.info("💡 **Professional Strategy Suite** - Configure and deploy institutional-grade trading strategies")
        
        strategy_choice = st.selectbox(
            "Select Strategy",
            ["Advanced Fibonacci Strategy", "ML Momentum Strategy", "RSI-EMA-ATR Strategy", "Z-Score Phi Strategy"]
        )
        
        if strategy_choice == "Advanced Fibonacci Strategy":
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("""
                <div class="flynt-card">
                    <h3>📐 Advanced Fibonacci Strategy</h3>
                    <p><strong>Mathematical Basis:</strong> Golden Ratio (φ = 1.618)</p>
                    <p><strong>Confidence Scoring:</strong> 0.6 - 1.0</p>
                    <p><strong>Best For:</strong> Swing Trading</p>
                    <h4 style="margin-top: 15px;">Fibonacci Levels</h4>
                    <ul>
                        <li><strong>0.236, 0.382, 0.500</strong> - Retracements</li>
                        <li><strong>0.618</strong> - Golden Ratio (Strong)</li>
                        <li><strong>0.786</strong> - Deep Retracement</li>
                        <li><strong>1.272, 1.618, 2.000</strong> - Extensions</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
                
                lookback = st.slider("Lookback Period", 20, 100, 50, key="fib_lookback")
                min_swing = st.slider("Min Swing Size (%)", 1.0, 5.0, 2.0, key="fib_swing") / 100
                confluence = st.slider("Confluence Threshold (%)", 0.5, 3.0, 1.5, key="fib_conf") / 100
                
                try:
                    config = {
                        'name': 'Fibonacci Strategy',
                        'lookback_period': lookback,
                        'min_swing_size': min_swing,
                        'confluence_threshold': confluence
                    }
                    strategy = AdvancedFibonacciStrategy(config)
                    st.success("✅ Strategy initialized successfully!")
                    
                    info = strategy.get_strategy_info()
                    metrics_cols = st.columns(4)
                    with metrics_cols[0]:
                        st.metric("Position", info.get('current_position', 0))
                    with metrics_cols[1]:
                        st.metric("Trades", info.get('total_trades', 0))
                    with metrics_cols[2]:
                        st.metric("Risk/Trade", f"{info.get('risk_per_trade', 0)*100:.1f}%")
                    with metrics_cols[3]:
                        st.metric("Max Position", f"{info.get('max_position_size', 0)*100:.1f}%")
                except Exception as e:
                    st.error(f"Strategy initialization error: {e}")
            
            with col2:
                st.markdown("""
                <div class="flynt-card">
                    <h4>📊 Strategy Status</h4>
                    <p>✅ Ready for deployment</p>
                    <p>🎯 Golden ratio levels active</p>
                    <p>📈 Multi-indicator confluence</p>
                </div>
                """, unsafe_allow_html=True)
        
        elif strategy_choice == "ML Momentum Strategy":
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("""
                <div class="flynt-card">
                    <h3>🤖 ML Momentum Strategy</h3>
                    <p><strong>Ensemble Method:</strong> Random Forest + Gradient Boosting</p>
                    <p><strong>Features:</strong> 20+ technical indicators</p>
                    <p><strong>Training:</strong> Real-time adaptive</p>
                    <h4 style="margin-top: 15px;">Feature Categories</h4>
                    <ul>
                        <li><strong>Momentum:</strong> 5, 10, 20 periods</li>
                        <li><strong>Oscillators:</strong> RSI, Stochastic, Williams %R</li>
                        <li><strong>Volume:</strong> Ratios & MFI</li>
                        <li><strong>Volatility:</strong> ATR, Bollinger</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
                
                lookback_ml = st.slider("Training Lookback", 50, 200, 100, key="ml_lookback")
                threshold = st.slider("Prediction Threshold", 0.5, 0.9, 0.6, key="ml_threshold")
                retrain = st.slider("Retrain Interval", 100, 1000, 500, key="ml_retrain")
                
                try:
                    config = {
                        'name': 'ML Momentum',
                        'lookback_period': lookback_ml,
                        'prediction_threshold': threshold,
                        'retrain_interval': retrain
                    }
                    ml_strategy = MLMomentumStrategy(config)
                    st.success("✅ ML Strategy initialized successfully!")
                    
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
                except Exception as e:
                    st.error(f"ML Strategy initialization error: {e}")
            
            with col2:
                st.markdown("""
                <div class="flynt-card">
                    <h4>🧠 Model Info</h4>
                    <p>✅ Ensemble ready</p>
                    <p>📊 20+ features</p>
                    <p>🔄 Auto-retraining</p>
                </div>
                """, unsafe_allow_html=True)

    # 📈 Portfolio Optimizer Tab
    with tab6:
        st.markdown('<h2 class="flynt-section">📈 Portfolio Optimization Tools</h2>', unsafe_allow_html=True)
        
        st.info("💡 **Professional Portfolio Management** - Modern Portfolio Theory optimization")
        
        opt_method = st.selectbox(
            "Optimization Method",
            ["Sharpe Ratio Maximization", "Kelly Criterion", "Minimum Variance", "Risk Parity", "Monte Carlo"]
        )
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            if opt_method == "Sharpe Ratio Maximization":
                st.markdown("""
                <div class="flynt-card">
                    <h3>📊 Sharpe Ratio Optimization</h3>
                    <p style="font-size: 1.1rem; text-align: center; padding: 15px;">
                        <strong>Sharpe = (R<sub>p</sub> - R<sub>f</sub>) / σ<sub>p</sub></strong>
                    </p>
                    <p><strong>R<sub>p</sub></strong> = Portfolio Return</p>
                    <p><strong>R<sub>f</sub></strong> = Risk-free Rate</p>
                    <p><strong>σ<sub>p</sub></strong> = Portfolio Std Dev</p>
                </div>
                """, unsafe_allow_html=True)
                
                risk_free_rate = st.slider("Risk-Free Rate (%)", 0.0, 10.0, 2.0) / 100
                
                st.success("✅ Optimization Complete!")
                metrics_cols = st.columns(4)
                with metrics_cols[0]:
                    st.metric("Expected Return", "15.2%", "+3.1%")
                with metrics_cols[1]:
                    st.metric("Volatility", "12.5%", "-2.0%")
                with metrics_cols[2]:
                    st.metric("Sharpe Ratio", "1.85", "+0.25")
                with metrics_cols[3]:
                    st.metric("Max Drawdown", "-8.2%", "+1.5%")
            
            elif opt_method == "Kelly Criterion":
                st.markdown("""
                <div class="flynt-card">
                    <h3>🎯 Kelly Criterion Position Sizing</h3>
                    <p style="font-size: 1.1rem; text-align: center; padding: 15px;">
                        <strong>f* = (bp - q) / b</strong>
                    </p>
                    <p><strong>p</strong> = Win Probability</p>
                    <p><strong>q</strong> = Loss Probability (1-p)</p>
                    <p><strong>b</strong> = Win/Loss Ratio</p>
                </div>
                """, unsafe_allow_html=True)
                
                col_a, col_b = st.columns(2)
                with col_a:
                    win_rate = st.slider("Win Rate (%)", 40.0, 80.0, 55.0, key="kelly_wr") / 100
                    avg_win = st.number_input("Average Win ($)", 100, 1000, 300, key="kelly_win")
                with col_b:
                    avg_loss = st.number_input("Average Loss ($)", 50, 500, 200, key="kelly_loss")
                    conservative = st.slider("Conservative Factor", 0.1, 1.0, 0.25, key="kelly_cons")
                
                win_loss_ratio = avg_win / avg_loss if avg_loss > 0 else 1.5
                kelly = (win_rate * win_loss_ratio - (1 - win_rate)) / win_loss_ratio
                conservative_kelly = kelly * conservative
                
                result_cols = st.columns(3)
                with result_cols[0]:
                    st.metric("Full Kelly", f"{kelly*100:.2f}%")
                with result_cols[1]:
                    st.metric("Conservative Kelly", f"{conservative_kelly*100:.2f}%")
                with result_cols[2]:
                    st.metric("Position ($10K)", f"${conservative_kelly*10000:.0f}")
                
                if kelly > 0:
                    st.success(f"✅ Positive Edge! Recommended: {conservative_kelly*100:.2f}%")
                else:
                    st.error("❌ Negative Edge - Do not trade!")
        
        with col2:
            st.markdown("""
            <div class="flynt-card">
                <h4>📚 About Portfolio Optimization</h4>
                <p>Modern Portfolio Theory helps maximize returns for given risk.</p>
                <h4 style="margin-top: 15px;">Methods Available</h4>
                <ul>
                    <li><strong>Sharpe:</strong> Risk-adjusted returns</li>
                    <li><strong>Kelly:</strong> Optimal sizing</li>
                    <li><strong>Min Variance:</strong> Lowest risk</li>
                    <li><strong>Risk Parity:</strong> Equal risk</li>
                    <li><strong>Monte Carlo:</strong> Scenarios</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

    # 📉 Strategy Comparison Tab
    with tab7:
        st.markdown('<h2 class="flynt-section">📉 Strategy Performance Comparison</h2>', unsafe_allow_html=True)
        
        st.info("💡 **Professional Analytics** - Compare performance across strategies")
        
        # Mock performance data
        strategies_data = {
            'Strategy': ['Fibonacci', 'ML Momentum', 'RSI-EMA-ATR', 'Z-Score Phi'],
            'Return (%)': [12.5, 15.8, 9.2, 11.0],
            'Sharpe': [1.75, 1.92, 1.45, 1.68],
            'Win Rate (%)': [58.0, 62.0, 52.0, 56.0],
            'Max DD (%)': [-8.2, -6.5, -10.5, -9.0],
            'Profit Factor': [1.85, 2.10, 1.55, 1.72],
            'Total Trades': [45, 38, 52, 41]
        }
        
        df_strategies = pd.DataFrame(strategies_data)
        
        st.dataframe(
            df_strategies.style.background_gradient(subset=['Return (%)', 'Sharpe'], cmap='Greens')
                               .background_gradient(subset=['Max DD (%)'], cmap='Reds_r'),
            use_container_width=True
        )
        
        # Performance chart
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=strategies_data['Strategy'],
            y=strategies_data['Return (%)'],
            name='Return %',
            marker_color='#187794'
        ))
        fig.update_layout(
            title='Strategy Returns Comparison',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font={'color': '#d0d0d0'}
        )
        st.plotly_chart(fig, use_container_width=True)

    # 🤖 ML Predictions Tab
    with tab8:
        st.markdown('<h2 class="flynt-section">🤖 Machine Learning Predictions</h2>', unsafe_allow_html=True)
        
        st.info("💡 **AI-Powered Forecasting** - Ensemble learning predictions")
        
        # Mock prediction data
        predictions = pd.DataFrame({
            'Asset': ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT', 'ADA/USDT'],
            'Current': [43250, 2280, 315, 98, 0.58],
            'Predicted': [44100, 2350, 320, 102, 0.60],
            'Change': ['+2.0%', '+3.1%', '+1.6%', '+4.1%', '+3.4%'],
            'Confidence': ['78%', '82%', '71%', '85%', '68%'],
            'Signal': ['BUY', 'BUY', 'HOLD', 'BUY', 'HOLD']
        })
        
        def color_signal(val):
            if val == 'BUY':
                return 'background-color: rgba(40, 167, 69, 0.3); color: #28a745'
            elif val == 'SELL':
                return 'background-color: rgba(220, 53, 69, 0.3); color: #dc3545'
            else:
                return 'background-color: rgba(255, 193, 7, 0.3); color: #ffc107'
        
        st.dataframe(
            predictions.style.applymap(color_signal, subset=['Signal']),
            use_container_width=True
        )
        
        # Feature importance
        st.markdown("### 🎯 Top Features")
        features_data = {
            'Feature': ['momentum_20', 'rsi', 'macd_histogram', 'price_to_sma20', 'volume_ratio'],
            'Importance': [0.15, 0.12, 0.11, 0.10, 0.09]
        }
        features_df = pd.DataFrame(features_data)
        
        fig = px.bar(features_df, x='Importance', y='Feature', orientation='h',
                     title='Feature Importance (Top 5)')
        fig.update_layout(template='plotly_dark', height=300)
        st.plotly_chart(fig, use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Training Samples", "1,250")
            st.metric("Feature Count", "23")
        with col2:
            st.metric("Ensemble Accuracy", "78.5%")
            st.metric("Predictions Made", "342")


# 🔄 Auto Refresh Logic
if auto_refresh:
    time.sleep(0.1)
    # st.rerun()  # Commented out to prevent infinite loop in demo

# 📱 FLYNT Footer
st.markdown("""
<div style="margin-top: 60px; padding: 30px 0; text-align: center; border-top: 1px solid var(--flynt-border); color: var(--flynt-content); font-family: 'Inter', sans-serif;">
    <h4 style="color: var(--flynt-secondary); font-family: 'Arimo', sans-serif; font-weight: 700; margin-bottom: 12px;">💎 CryptoBot Professional</h4>
    <p style="font-size: 0.875rem; margin: 4px 0;">FLYNT-Inspired Design | Advanced Trading Intelligence</p>
    <p style="font-size: 0.8rem; opacity: 0.7;">⚡ Real-time Data • 🔒 Secure Trading • 📊 Professional Analytics</p>
    <p style="font-size: 0.75rem; margin-top: 16px; opacity: 0.6;">© 2025 CryptoBot Pro | Built with Streamlit</p>
</div>
""", unsafe_allow_html=True)
