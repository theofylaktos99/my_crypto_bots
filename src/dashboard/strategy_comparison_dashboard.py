# strategy_comparison_dashboard.py - Professional Strategy Comparison & Analysis
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class StrategyComparisonDashboard:
    """
    Professional dashboard for comparing and analyzing trading strategies
    """
    
    def __init__(self):
        self.strategies_data = {}
        self.comparison_metrics = [
            'total_return', 'sharpe_ratio', 'win_rate', 'max_drawdown',
            'profit_factor', 'total_trades', 'average_return'
        ]
    
    def render_strategy_overview(self, strategies: Dict[str, Any]):
        """Render strategy overview section"""
        st.markdown("## 📊 Strategy Performance Overview")
        
        # Create metrics grid
        cols = st.columns(4)
        
        # Calculate aggregate metrics
        total_strategies = len(strategies)
        active_strategies = sum(1 for s in strategies.values() if s.get('is_active', False))
        total_trades = sum(s.get('total_trades', 0) for s in strategies.values())
        avg_win_rate = np.mean([s.get('win_rate', 0) for s in strategies.values()])
        
        with cols[0]:
            st.metric("Total Strategies", total_strategies, 
                     delta=f"+{len(strategies) - 5} new" if len(strategies) > 5 else None)
        
        with cols[1]:
            st.metric("Active Strategies", active_strategies,
                     delta="Running" if active_strategies > 0 else "Inactive")
        
        with cols[2]:
            st.metric("Total Trades", f"{total_trades:,}",
                     delta="+15% this week" if total_trades > 100 else None)
        
        with cols[3]:
            st.metric("Avg Win Rate", f"{avg_win_rate:.1f}%",
                     delta=f"+{avg_win_rate - 50:.1f}%" if avg_win_rate > 50 else f"{avg_win_rate - 50:.1f}%")
    
    def render_performance_comparison(self, strategies_performance: Dict[str, Dict]):
        """Render detailed performance comparison"""
        st.markdown("### 📈 Performance Comparison")
        
        if not strategies_performance:
            st.info("No strategy performance data available")
            return
        
        # Create comparison DataFrame
        comparison_data = []
        for strategy_name, metrics in strategies_performance.items():
            row = {
                'Strategy': strategy_name,
                'Return (%)': metrics.get('total_return', 0),
                'Sharpe Ratio': metrics.get('sharpe_ratio', 0),
                'Win Rate (%)': metrics.get('win_rate', 0),
                'Max DD (%)': metrics.get('max_drawdown', 0),
                'Profit Factor': metrics.get('profit_factor', 0),
                'Trades': metrics.get('total_trades', 0)
            }
            comparison_data.append(row)
        
        df = pd.DataFrame(comparison_data)
        
        # Display as styled dataframe
        st.dataframe(
            df.style.background_gradient(subset=['Return (%)', 'Sharpe Ratio', 'Win Rate (%)'], cmap='RdYlGn')
                    .background_gradient(subset=['Max DD (%)'], cmap='RdYlGn_r')
                    .format({
                        'Return (%)': '{:.2f}',
                        'Sharpe Ratio': '{:.2f}',
                        'Win Rate (%)': '{:.1f}',
                        'Max DD (%)': '{:.2f}',
                        'Profit Factor': '{:.2f}',
                        'Trades': '{:.0f}'
                    }),
            use_container_width=True
        )
        
        # Create comparison charts
        self._render_comparison_charts(df)
    
    def _render_comparison_charts(self, df: pd.DataFrame):
        """Render comparison visualization charts"""
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Returns Comparison', 'Risk-Adjusted Returns (Sharpe)',
                          'Win Rate Analysis', 'Risk vs Return'),
            specs=[[{'type': 'bar'}, {'type': 'bar'}],
                   [{'type': 'bar'}, {'type': 'scatter'}]]
        )
        
        # Returns comparison
        fig.add_trace(
            go.Bar(x=df['Strategy'], y=df['Return (%)'],
                   name='Return', marker_color='lightblue'),
            row=1, col=1
        )
        
        # Sharpe ratio comparison
        fig.add_trace(
            go.Bar(x=df['Strategy'], y=df['Sharpe Ratio'],
                   name='Sharpe', marker_color='lightgreen'),
            row=1, col=2
        )
        
        # Win rate comparison
        fig.add_trace(
            go.Bar(x=df['Strategy'], y=df['Win Rate (%)'],
                   name='Win Rate', marker_color='lightyellow'),
            row=2, col=1
        )
        
        # Risk vs Return scatter
        fig.add_trace(
            go.Scatter(
                x=abs(df['Max DD (%)']), 
                y=df['Return (%)'],
                mode='markers+text',
                text=df['Strategy'],
                textposition='top center',
                marker=dict(size=df['Sharpe Ratio']*5+10, color=df['Sharpe Ratio'],
                          colorscale='Viridis', showscale=True),
                name='Strategies'
            ),
            row=2, col=2
        )
        
        # Update layout
        fig.update_xaxes(title_text="Strategy", row=1, col=1)
        fig.update_xaxes(title_text="Strategy", row=1, col=2)
        fig.update_xaxes(title_text="Strategy", row=2, col=1)
        fig.update_xaxes(title_text="Max Drawdown (%)", row=2, col=2)
        
        fig.update_yaxes(title_text="Return (%)", row=1, col=1)
        fig.update_yaxes(title_text="Sharpe Ratio", row=1, col=2)
        fig.update_yaxes(title_text="Win Rate (%)", row=2, col=1)
        fig.update_yaxes(title_text="Return (%)", row=2, col=2)
        
        fig.update_layout(
            height=800,
            showlegend=False,
            template='plotly_dark'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def render_equity_curves(self, equity_data: Dict[str, pd.Series]):
        """Render equity curves for all strategies"""
        st.markdown("### 📉 Equity Curves Comparison")
        
        if not equity_data:
            st.info("No equity curve data available")
            return
        
        fig = go.Figure()
        
        for strategy_name, equity_series in equity_data.items():
            fig.add_trace(go.Scatter(
                x=equity_series.index,
                y=equity_series.values,
                name=strategy_name,
                mode='lines',
                line=dict(width=2)
            ))
        
        fig.update_layout(
            title='Strategy Equity Curves Over Time',
            xaxis_title='Date',
            yaxis_title='Equity Value',
            template='plotly_dark',
            height=500,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def render_drawdown_analysis(self, drawdown_data: Dict[str, pd.Series]):
        """Render drawdown analysis"""
        st.markdown("### 📊 Drawdown Analysis")
        
        if not drawdown_data:
            st.info("No drawdown data available")
            return
        
        fig = go.Figure()
        
        for strategy_name, drawdown_series in drawdown_data.items():
            fig.add_trace(go.Scatter(
                x=drawdown_series.index,
                y=drawdown_series.values * 100,  # Convert to percentage
                name=strategy_name,
                fill='tozeroy',
                mode='lines'
            ))
        
        fig.update_layout(
            title='Drawdown Over Time',
            xaxis_title='Date',
            yaxis_title='Drawdown (%)',
            template='plotly_dark',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def render_monthly_returns_heatmap(self, returns_data: Dict[str, pd.DataFrame]):
        """Render monthly returns heatmap"""
        st.markdown("### 🔥 Monthly Returns Heatmap")
        
        if not returns_data:
            st.info("No monthly returns data available")
            return
        
        # Select strategy
        strategy_names = list(returns_data.keys())
        selected_strategy = st.selectbox("Select Strategy", strategy_names)
        
        if selected_strategy and selected_strategy in returns_data:
            monthly_returns = returns_data[selected_strategy]
            
            # Create heatmap
            fig = go.Figure(data=go.Heatmap(
                z=monthly_returns.values,
                x=monthly_returns.columns,
                y=monthly_returns.index,
                colorscale='RdYlGn',
                text=monthly_returns.values,
                texttemplate='%{text:.1f}%',
                textfont={"size": 10},
                colorbar=dict(title="Return (%)")
            ))
            
            fig.update_layout(
                title=f'{selected_strategy} - Monthly Returns',
                xaxis_title='Month',
                yaxis_title='Year',
                height=400,
                template='plotly_dark'
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    def render_risk_metrics(self, risk_metrics: Dict[str, Dict]):
        """Render comprehensive risk metrics"""
        st.markdown("### ⚠️ Risk Metrics Dashboard")
        
        if not risk_metrics:
            st.info("No risk metrics available")
            return
        
        # Create risk metrics table
        risk_data = []
        for strategy_name, metrics in risk_metrics.items():
            risk_data.append({
                'Strategy': strategy_name,
                'Volatility (%)': metrics.get('volatility', 0) * 100,
                'Max DD (%)': abs(metrics.get('max_drawdown', 0)),
                'VaR 95% (%)': abs(metrics.get('var_95', 0)) * 100,
                'CVaR 95% (%)': abs(metrics.get('cvar_95', 0)) * 100,
                'Sortino Ratio': metrics.get('sortino_ratio', 0),
                'Calmar Ratio': metrics.get('calmar_ratio', 0)
            })
        
        risk_df = pd.DataFrame(risk_data)
        
        st.dataframe(
            risk_df.style.background_gradient(subset=['Volatility (%)', 'Max DD (%)', 'VaR 95% (%)', 'CVaR 95% (%)'], 
                                             cmap='Reds')
                        .background_gradient(subset=['Sortino Ratio', 'Calmar Ratio'], cmap='Greens')
                        .format({
                            'Volatility (%)': '{:.2f}',
                            'Max DD (%)': '{:.2f}',
                            'VaR 95% (%)': '{:.2f}',
                            'CVaR 95% (%)': '{:.2f}',
                            'Sortino Ratio': '{:.2f}',
                            'Calmar Ratio': '{:.2f}'
                        }),
            use_container_width=True
        )
    
    def render_trade_analysis(self, trade_data: Dict[str, List[Dict]]):
        """Render detailed trade analysis"""
        st.markdown("### 💼 Trade Analysis")
        
        if not trade_data:
            st.info("No trade data available")
            return
        
        # Select strategy
        strategy_names = list(trade_data.keys())
        selected_strategy = st.selectbox("Select Strategy for Trade Analysis", strategy_names, key='trade_analysis')
        
        if selected_strategy and selected_strategy in trade_data:
            trades = trade_data[selected_strategy]
            
            if not trades:
                st.info(f"No trades available for {selected_strategy}")
                return
            
            trades_df = pd.DataFrame(trades)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Trade Distribution")
                
                # Win/Loss distribution
                fig_dist = go.Figure()
                win_trades = trades_df[trades_df['pnl_percent'] > 0]
                loss_trades = trades_df[trades_df['pnl_percent'] <= 0]
                
                fig_dist.add_trace(go.Box(y=win_trades['pnl_percent'], name='Winning Trades', 
                                         marker_color='green'))
                fig_dist.add_trace(go.Box(y=loss_trades['pnl_percent'], name='Losing Trades',
                                         marker_color='red'))
                
                fig_dist.update_layout(
                    title='Trade P&L Distribution',
                    yaxis_title='P&L (%)',
                    template='plotly_dark',
                    height=300
                )
                
                st.plotly_chart(fig_dist, use_container_width=True)
            
            with col2:
                st.subheader("Cumulative P&L")
                
                # Cumulative P&L
                trades_df['cumulative_pnl'] = trades_df['pnl_percent'].cumsum()
                
                fig_cum = go.Figure()
                fig_cum.add_trace(go.Scatter(
                    x=list(range(len(trades_df))),
                    y=trades_df['cumulative_pnl'],
                    mode='lines',
                    fill='tozeroy',
                    line=dict(color='cyan', width=2)
                ))
                
                fig_cum.update_layout(
                    title='Cumulative P&L Over Trades',
                    xaxis_title='Trade Number',
                    yaxis_title='Cumulative P&L (%)',
                    template='plotly_dark',
                    height=300
                )
                
                st.plotly_chart(fig_cum, use_container_width=True)
            
            # Trade table
            st.subheader("Recent Trades")
            st.dataframe(
                trades_df.tail(20).style.apply(
                    lambda x: ['background-color: rgba(0,255,0,0.2)' if v > 0 
                              else 'background-color: rgba(255,0,0,0.2)' 
                              for v in x], 
                    subset=['pnl_percent']
                ),
                use_container_width=True
            )
    
    def render_strategy_correlation(self, correlation_matrix: pd.DataFrame):
        """Render strategy correlation heatmap"""
        st.markdown("### 🔗 Strategy Correlation Analysis")
        
        if correlation_matrix is None or correlation_matrix.empty:
            st.info("No correlation data available")
            return
        
        fig = go.Figure(data=go.Heatmap(
            z=correlation_matrix.values,
            x=correlation_matrix.columns,
            y=correlation_matrix.index,
            colorscale='RdBu',
            zmid=0,
            text=correlation_matrix.values,
            texttemplate='%{text:.2f}',
            textfont={"size": 10},
            colorbar=dict(title="Correlation")
        ))
        
        fig.update_layout(
            title='Strategy Returns Correlation Matrix',
            height=500,
            template='plotly_dark'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.info("💡 **Tip**: Low correlation between strategies indicates better diversification")
    
    def render_recommendations(self, analysis_results: Dict[str, Any]):
        """Render AI-powered strategy recommendations"""
        st.markdown("### 🤖 AI Strategy Recommendations")
        
        st.markdown("""
        <div style='background: linear-gradient(135deg, rgba(24,119,148,0.1), rgba(109,178,199,0.1)); 
                    border-left: 4px solid #187794; padding: 20px; border-radius: 8px; margin: 20px 0;'>
            <h4 style='color: #6db2c7; margin-top: 0;'>💡 Smart Recommendations</h4>
        """, unsafe_allow_html=True)
        
        if not analysis_results:
            st.info("Run analysis to get recommendations")
            st.markdown("</div>", unsafe_allow_html=True)
            return
        
        # Top performing strategy
        if 'best_strategy' in analysis_results:
            st.success(f"🏆 **Best Performer**: {analysis_results['best_strategy']} with {analysis_results.get('best_return', 0):.2f}% return")
        
        # Diversification recommendation
        if 'diversification_score' in analysis_results:
            score = analysis_results['diversification_score']
            if score > 0.7:
                st.success(f"✅ **Excellent Diversification**: Portfolio correlation score {score:.2f}")
            elif score > 0.4:
                st.warning(f"⚠️ **Moderate Diversification**: Consider adding uncorrelated strategies (score: {score:.2f})")
            else:
                st.error(f"❌ **Poor Diversification**: High correlation between strategies (score: {score:.2f})")
        
        # Risk recommendation
        if 'risk_level' in analysis_results:
            risk = analysis_results['risk_level']
            if risk == 'low':
                st.info("🛡️ **Low Risk Profile**: Current portfolio has conservative risk levels")
            elif risk == 'medium':
                st.info("⚖️ **Balanced Risk Profile**: Good balance between risk and return")
            else:
                st.warning("⚠️ **High Risk Profile**: Consider reducing position sizes or adding hedging strategies")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    def render_full_dashboard(self, strategies_data: Dict[str, Any]):
        """Render complete strategy comparison dashboard"""
        try:
            # Header
            st.markdown("""
            <div style='text-align: center; padding: 30px 0;'>
                <h1 style='background: linear-gradient(135deg, #187794, #6db2c7); 
                          -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                          font-size: 3rem; font-weight: 700;'>
                    🎯 Strategy Comparison Dashboard
                </h1>
                <p style='color: #d0d0d0; font-size: 1.2rem; opacity: 0.8;'>
                    Professional Trading Strategy Analysis & Optimization
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Strategy overview
            self.render_strategy_overview(strategies_data.get('strategies', {}))
            
            st.markdown("---")
            
            # Performance comparison
            if 'performance' in strategies_data:
                self.render_performance_comparison(strategies_data['performance'])
            
            st.markdown("---")
            
            # Equity curves
            if 'equity_curves' in strategies_data:
                self.render_equity_curves(strategies_data['equity_curves'])
            
            st.markdown("---")
            
            # Risk metrics
            if 'risk_metrics' in strategies_data:
                self.render_risk_metrics(strategies_data['risk_metrics'])
            
            st.markdown("---")
            
            # Drawdown analysis
            if 'drawdowns' in strategies_data:
                self.render_drawdown_analysis(strategies_data['drawdowns'])
            
            st.markdown("---")
            
            # Trade analysis
            if 'trades' in strategies_data:
                self.render_trade_analysis(strategies_data['trades'])
            
            st.markdown("---")
            
            # Correlation analysis
            if 'correlation' in strategies_data:
                self.render_strategy_correlation(strategies_data['correlation'])
            
            st.markdown("---")
            
            # Recommendations
            if 'recommendations' in strategies_data:
                self.render_recommendations(strategies_data['recommendations'])
            
        except Exception as e:
            logger.error(f"Error rendering dashboard: {e}")
            st.error(f"Error rendering dashboard: {str(e)}")
