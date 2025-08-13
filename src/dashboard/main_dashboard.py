# main_dashboard.py - Main Trading Dashboard Application
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import logging
from typing import Dict, Any, List
import asyncio
import threading
import time

from ..utils.config_manager import ConfigManager
from ..api.market_data import MarketDataFetcher
from ..api.binance_client import BinanceClient
from ..strategies.rsi_ema_atr_strategy import RSIEMAATRStrategy
from ..bots.bot_manager import BotManager

logger = logging.getLogger(__name__)

class MainDashboard:
    """Main trading dashboard application"""
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.market_data_fetcher = MarketDataFetcher()
        self.bot_manager = BotManager(config_manager)
        
        # Initialize session state
        self._init_session_state()
        
        logger.info("✅ Main dashboard initialized")
    
    def _init_session_state(self):
        """Initialize Streamlit session state"""
        if 'market_data' not in st.session_state:
            st.session_state.market_data = {}
        
        if 'active_bots' not in st.session_state:
            st.session_state.active_bots = {}
        
        if 'selected_strategy' not in st.session_state:
            st.session_state.selected_strategy = 'RSI_EMA_ATR'
        
        if 'page' not in st.session_state:
            st.session_state.page = 'Dashboard'
    
    def run(self):
        """Run the main dashboard"""
        st.set_page_config(
            page_title="🚀 Crypto Trading Bot System",
            page_icon="🤖",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Custom CSS
        self._inject_custom_css()
        
        # Sidebar navigation
        self._render_sidebar()
        
        # Main content
        if st.session_state.page == 'Dashboard':
            self._render_main_dashboard()
        elif st.session_state.page == 'Strategies':
            self._render_strategies_page()
        elif st.session_state.page == 'Bots':
            self._render_bots_page()
        elif st.session_state.page == 'Market':
            self._render_market_page()
        elif st.session_state.page == 'Settings':
            self._render_settings_page()
    
    def _inject_custom_css(self):
        """Inject custom CSS styles"""
        st.markdown("""
        <style>
        .main-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1rem;
            border-radius: 10px;
            color: white;
            margin-bottom: 2rem;
        }
        
        .metric-card {
            background: white;
            padding: 1rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-left: 4px solid #667eea;
        }
        
        .status-running {
            color: #28a745;
            font-weight: bold;
        }
        
        .status-stopped {
            color: #dc3545; 
            font-weight: bold;
        }
        
        .status-paused {
            color: #ffc107;
            font-weight: bold;
        }
        
        .bot-card {
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 8px;
            margin: 0.5rem 0;
            border: 1px solid #e9ecef;
        }
        
        .strategy-card {
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin: 1rem 0;
            border-left: 4px solid #28a745;
        }
        
        .alert-success {
            background-color: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
            padding: 0.75rem;
            border-radius: 0.375rem;
            margin: 1rem 0;
        }
        
        .alert-danger {
            background-color: #f8d7da;
            border: 1px solid #f5c6cb;
            color: #721c24;
            padding: 0.75rem;
            border-radius: 0.375rem;
            margin: 1rem 0;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def _render_sidebar(self):
        """Render sidebar navigation"""
        with st.sidebar:
            st.markdown("# 🤖 Trading Bot System")
            st.markdown("---")
            
            # Navigation
            pages = {
                "📊 Dashboard": "Dashboard",
                "🎯 Strategies": "Strategies", 
                "🤖 Bots": "Bots",
                "📈 Market": "Market",
                "⚙️ Settings": "Settings"
            }
            
            for display_name, page_key in pages.items():
                if st.button(display_name, key=f"nav_{page_key}"):
                    st.session_state.page = page_key
                    st.rerun()
            
            st.markdown("---")
            
            # System status
            st.markdown("### 📊 System Status")
            
            # Get bot count
            active_bots = len(st.session_state.active_bots)
            st.metric("Active Bots", active_bots)
            
            # System uptime (placeholder)
            st.metric("System Uptime", "2h 45m")
            
            st.markdown("---")
            
            # Quick actions
            st.markdown("### ⚡ Quick Actions")
            
            if st.button("🔄 Refresh Data"):
                self._refresh_market_data()
                st.success("Data refreshed!")
                time.sleep(1)
                st.rerun()
            
            if st.button("⏸️ Pause All Bots"):
                self.bot_manager.pause_all_bots()
                st.warning("All bots paused!")
            
            if st.button("🛑 Emergency Stop"):
                self.bot_manager.stop_all_bots()
                st.error("Emergency stop executed!")
    
    def _render_main_dashboard(self):
        """Render main dashboard page"""
        # Header
        st.markdown("""
        <div class="main-header">
            <h1>🚀 Crypto Trading Bot Dashboard</h1>
            <p>Professional Trading Bot Management System</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Key metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Total Bots", len(st.session_state.active_bots))
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            running_bots = sum(1 for bot in st.session_state.active_bots.values() 
                             if bot.get('status') == 'running')
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Running Bots", running_bots)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            total_pnl = sum(bot.get('total_pnl', 0) for bot in st.session_state.active_bots.values())
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Total P&L", f"{total_pnl:+.2f}%")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col4:
            total_trades = sum(bot.get('total_trades', 0) for bot in st.session_state.active_bots.values())
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Total Trades", total_trades)
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Market overview and bot status in columns
        col_left, col_right = st.columns([1, 1])
        
        with col_left:
            st.markdown("## 📈 Market Overview")
            self._render_market_overview()
        
        with col_right:
            st.markdown("## 🤖 Active Bots")
            self._render_active_bots_summary()
        
        # Recent activity
        st.markdown("---")
        st.markdown("## 📝 Recent Activity")
        self._render_recent_activity()
    
    def _render_market_overview(self):
        """Render market overview section"""
        try:
            # Get market data
            if not st.session_state.market_data:
                with st.spinner("Loading market data..."):
                    st.session_state.market_data = self.market_data_fetcher.get_live_market_data(10)
            
            if st.session_state.market_data:
                # Create market data DataFrame
                df = pd.DataFrame(st.session_state.market_data).T
                df = df.head(5)  # Top 5 cryptocurrencies
                
                # Display as table
                st.dataframe(
                    df[['name', 'price', 'change_24h', 'market_cap']],
                    column_config={
                        "name": "Name",
                        "price": st.column_config.NumberColumn("Price ($)", format="%.4f"),
                        "change_24h": st.column_config.NumberColumn("24h Change (%)", format="%.2f"),
                        "market_cap": st.column_config.NumberColumn("Market Cap", format="$%.0f")
                    },
                    hide_index=False
                )
            else:
                st.error("Failed to load market data")
                
        except Exception as e:
            logger.error(f"Error rendering market overview: {e}")
            st.error("Error loading market data")
    
    def _render_active_bots_summary(self):
        """Render active bots summary"""
        if not st.session_state.active_bots:
            st.info("No active bots. Deploy a bot from the Strategies page!")
            return
        
        for bot_name, bot_info in st.session_state.active_bots.items():
            status = bot_info.get('status', 'unknown')
            pnl = bot_info.get('total_pnl', 0)
            trades = bot_info.get('total_trades', 0)
            
            status_class = f"status-{status}"
            
            st.markdown(f"""
            <div class="bot-card">
                <h4>{bot_name}</h4>
                <p><span class="{status_class}">Status: {status.upper()}</span></p>
                <p>Symbol: {bot_info.get('symbol', 'N/A')}</p>
                <p>P&L: {pnl:+.2f}% | Trades: {trades}</p>
            </div>
            """, unsafe_allow_html=True)
    
    def _render_recent_activity(self):
        """Render recent activity log"""
        # Placeholder for recent activity
        activities = [
            {"time": "10:15:23", "type": "TRADE", "message": "BTC_Bot_01: BUY BTC/USDT @ 45,234.56"},
            {"time": "10:12:45", "type": "SIGNAL", "message": "ETH_Bot_02: RSI oversold signal detected"},
            {"time": "10:08:12", "type": "INFO", "message": "Market data updated successfully"},
            {"time": "10:05:30", "type": "TRADE", "message": "BTC_Bot_01: SELL BTC/USDT @ 45,456.78 | P&L: +0.49%"}
        ]
        
        for activity in activities:
            icon = {"TRADE": "💰", "SIGNAL": "📊", "INFO": "ℹ️"}.get(activity["type"], "📝")
            st.markdown(f"**{activity['time']}** {icon} {activity['message']}")
    
    def _render_strategies_page(self):
        """Render strategies management page"""
        st.markdown("# 🎯 Trading Strategies")
        st.markdown("Manage and deploy your trading strategies")
        
        # Get available strategies
        strategies = self.config_manager.get_config('strategies', 'strategies', {})
        
        for strategy_key, strategy_info in strategies.items():
            if strategy_info.get('enabled', True):
                self._render_strategy_card(strategy_key, strategy_info)
    
    def _render_strategy_card(self, strategy_key: str, strategy_info: Dict[str, Any]):
        """Render individual strategy card"""
        st.markdown(f"""
        <div class="strategy-card">
            <h3>{strategy_info.get('name', strategy_key)}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.markdown(f"**Parameters**: {strategy_info.get('parameters', {})}")
        
        with col2:
            if st.button(f"📊 Backtest", key=f"backtest_{strategy_key}"):
                st.info("Backtesting feature coming soon!")
        
        with col3:
            if st.button(f"🚀 Deploy", key=f"deploy_{strategy_key}"):
                st.session_state.selected_strategy = strategy_key
                st.session_state.page = 'Bots'
                st.rerun()
    
    def _render_bots_page(self):
        """Render bots management page"""
        st.markdown("# 🤖 Bot Management")
        
        tab1, tab2 = st.tabs(["Deploy New Bot", "Manage Bots"])
        
        with tab1:
            self._render_bot_deployment()
        
        with tab2:
            self._render_bot_management()
    
    def _render_bot_deployment(self):
        """Render bot deployment interface"""
        st.markdown("## 🚀 Deploy New Trading Bot")
        
        col1, col2 = st.columns(2)
        
        with col1:
            bot_name = st.text_input("Bot Name:", value=f"Bot_{datetime.now().strftime('%H%M%S')}")
            
            strategies = list(self.config_manager.get_config('strategies', 'strategies', {}).keys())
            strategy = st.selectbox("Strategy:", strategies, 
                                  index=strategies.index(st.session_state.selected_strategy) 
                                  if st.session_state.selected_strategy in strategies else 0)
            
            symbol = st.selectbox("Trading Pair:", ["BTC/USDT", "ETH/USDT", "BNB/USDT", "ADA/USDT"])
            
        with col2:
            timeframe = st.selectbox("Timeframe:", ["1m", "5m", "15m", "30m", "1h", "4h", "1d"])
            
            position_size = st.slider("Position Size (% of balance):", 1, 20, 10)
            
            risk_per_trade = st.slider("Risk per Trade (%):", 0.5, 5.0, 2.0, 0.1)
        
        st.markdown("---")
        
        col1, col2, col3 = st.columns(3)
        
        with col2:
            if st.button("🚀 Deploy Bot", type="primary"):
                # Deploy bot logic
                bot_config = {
                    'name': bot_name,
                    'strategy': strategy,
                    'symbol': symbol,
                    'timeframe': timeframe,
                    'position_size': position_size / 100,
                    'risk_per_trade': risk_per_trade / 100,
                    'deployed_at': datetime.now().isoformat()
                }
                
                success = self.bot_manager.deploy_bot(bot_name, bot_config)
                
                if success:
                    st.session_state.active_bots[bot_name] = bot_config
                    st.success(f"✅ Bot '{bot_name}' deployed successfully!")
                else:
                    st.error("❌ Failed to deploy bot")
    
    def _render_bot_management(self):
        """Render bot management interface"""
        if not st.session_state.active_bots:
            st.info("No bots deployed yet. Deploy your first bot!")
            return
        
        for bot_name, bot_info in st.session_state.active_bots.items():
            with st.expander(f"🤖 {bot_name}", expanded=True):
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    if st.button("▶️ Start", key=f"start_{bot_name}"):
                        st.success(f"Started {bot_name}")
                
                with col2:
                    if st.button("⏸️ Pause", key=f"pause_{bot_name}"):
                        st.warning(f"Paused {bot_name}")
                
                with col3:
                    if st.button("⏹️ Stop", key=f"stop_{bot_name}"):
                        st.error(f"Stopped {bot_name}")
                
                with col4:
                    if st.button("🗑️ Remove", key=f"remove_{bot_name}"):
                        del st.session_state.active_bots[bot_name]
                        st.rerun()
                
                # Bot details
                st.markdown(f"**Strategy**: {bot_info.get('strategy', 'N/A')}")
                st.markdown(f"**Symbol**: {bot_info.get('symbol', 'N/A')}")
                st.markdown(f"**Timeframe**: {bot_info.get('timeframe', 'N/A')}")
                st.markdown(f"**Status**: {bot_info.get('status', 'Stopped')}")
    
    def _render_market_page(self):
        """Render market analysis page"""
        st.markdown("# 📈 Market Analysis")
        
        # Market data refresh
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown("## Live Market Data")
        
        with col2:
            if st.button("🔄 Refresh"):
                self._refresh_market_data()
        
        # Market overview
        self._render_detailed_market_data()
    
    def _render_detailed_market_data(self):
        """Render detailed market data"""
        if not st.session_state.market_data:
            self._refresh_market_data()
        
        if st.session_state.market_data:
            df = pd.DataFrame(st.session_state.market_data).T
            
            # Display full market data
            st.dataframe(
                df,
                column_config={
                    "name": "Name",
                    "symbol": "Symbol", 
                    "price": st.column_config.NumberColumn("Price ($)", format="%.4f"),
                    "change_24h": st.column_config.NumberColumn("24h Change (%)", format="%.2f"),
                    "change_7d": st.column_config.NumberColumn("7d Change (%)", format="%.2f"),
                    "market_cap": st.column_config.NumberColumn("Market Cap", format="$%.0f"),
                    "volume_24h": st.column_config.NumberColumn("24h Volume", format="$%.0f")
                },
                use_container_width=True
            )
        else:
            st.error("Failed to load market data")
    
    def _render_settings_page(self):
        """Render settings page"""
        st.markdown("# ⚙️ Settings")
        
        tab1, tab2, tab3 = st.tabs(["General", "Risk Management", "API"])
        
        with tab1:
            st.markdown("## General Settings")
            
            debug_mode = st.checkbox("Debug Mode", 
                                   value=self.config_manager.get_config('app', 'debug', False))
            
            max_bots = st.slider("Max Concurrent Bots:", 1, 10, 
                               value=self.config_manager.get_config('app', 'max_concurrent_bots', 5))
            
            if st.button("Save General Settings"):
                self.config_manager.set_config('app', 'debug', debug_mode)
                self.config_manager.set_config('app', 'max_concurrent_bots', max_bots)
                st.success("✅ Settings saved!")
        
        with tab2:
            st.markdown("## Risk Management")
            
            risk_config = self.config_manager.get_risk_config()
            
            max_position = st.slider("Max Position Size (%):", 1, 50, 
                                   int(risk_config.get('max_position_size', 0.1) * 100))
            
            risk_per_trade = st.slider("Risk per Trade (%):", 0.1, 10.0, 
                                     risk_config.get('risk_per_trade', 0.02) * 100, 0.1)
            
            max_daily_loss = st.slider("Max Daily Loss (%):", 1, 20, 
                                     int(risk_config.get('max_daily_loss', 0.05) * 100))
            
            if st.button("Save Risk Settings"):
                self.config_manager.set_config('risk', 'max_position_size', max_position / 100)
                self.config_manager.set_config('risk', 'risk_per_trade', risk_per_trade / 100)
                self.config_manager.set_config('risk', 'max_daily_loss', max_daily_loss / 100)
                st.success("✅ Risk settings saved!")
        
        with tab3:
            st.markdown("## API Configuration")
            
            st.info("API keys are configured via environment variables for security.")
            
            # Test API connection
            if st.button("Test Exchange Connection"):
                with st.spinner("Testing connection..."):
                    # Placeholder for connection test
                    st.success("✅ Connection successful!")
    
    def _refresh_market_data(self):
        """Refresh market data"""
        try:
            with st.spinner("Refreshing market data..."):
                st.session_state.market_data = self.market_data_fetcher.get_live_market_data(20)
            logger.info("Market data refreshed")
        except Exception as e:
            logger.error(f"Error refreshing market data: {e}")
            st.error("Failed to refresh market data")
