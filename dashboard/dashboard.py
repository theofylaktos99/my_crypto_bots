# dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px
import os
import time
from datetime import datetime

# === Ρυθμίσεις ===
LOG_FILE_PATH = r"c:\DEV PORTOFOLIO\my_crypto_bots\test_data.csv"
REFRESH_INTERVAL = 10  # δευτερόλεπτα

# === Streamlit Layout και Μαύρο/Πράσινο Matrix Theme ===
st.set_page_config(page_title="MatrixBot Dashboard", layout="wide")
st.markdown(
    """
    <style>
    html, body, [class*="css"] {
        background-color: black;
        color: #00FF00;
        font-family: 'Courier New', Courier, monospace;
    }
    .stMetric {
        background-color: #003300;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 0 10px #00FF00;
    }
    .stMetric:hover {
        transform: scale(1.05);
        box-shadow: 0 0 20px #00FF00;
    }
    .block-container {
        padding-top: 2rem;
    }
    h1, h2, h3 {
        color: #00FF00;
    }
    .glow-line {
        width: 100%;
        height: 2px;
        background: linear-gradient(to right, #00FF00, #003300);
        box-shadow: 0 0 10px #00FF00;
        margin-top: 20px;
        margin-bottom: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# === Τίτλος ===
st.markdown('<h1>🧠 MatrixBot Live Dashboard</h1>', unsafe_allow_html=True)
st.markdown('<div class="glow-line"></div>', unsafe_allow_html=True)

# === Live Ενημέρωση ===
hud = st.empty()

with hud:
    while True:
        try:
            # === Διαβάζουμε το CSV αρχείο ===
            df = pd.read_csv(LOG_FILE_PATH)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df.sort_values('timestamp', inplace=True)

            # === Υπολογιστικά Στοιχεία ===
            closed_trades = df[df['action'].str.contains("SELL")].copy()
            wins = closed_trades[closed_trades['pnl'] > 0]
            losses = closed_trades[closed_trades['pnl'] <= 0]
            avg_pnl_pct = closed_trades['pnl_percent'].mean() if not closed_trades.empty else 0.0
            winrate = (len(wins) / len(closed_trades)) * 100 if not closed_trades.empty else 0.0

            col1, col2, col3 = st.columns(3)
            col1.metric("🚀 Κλειστά Trades", f"{len(closed_trades)}")
            col2.metric("✅ Win Rate", f"{winrate:.2f}%")
            col3.metric("📈 Μέσο PnL %", f"{avg_pnl_pct:.2f}%")

            st.markdown('<div class="glow-line"></div>', unsafe_allow_html=True)

            st.markdown("### 📜 Πρόσφατα Trades")
            st.dataframe(df.tail(15), use_container_width=True)

            st.markdown('<div class="glow-line"></div>', unsafe_allow_html=True)

            # === Γραφήματα Απόδοσης ===
            if not closed_trades.empty:
                fig1 = px.line(
                    closed_trades,
                    x='timestamp',
                    y='pnl',
                    title="PnL Ανά Trade",
                    template="plotly_dark",
                    markers=True,
                    color_discrete_sequence=["#00FF00"],
                )
                st.plotly_chart(fig1, use_container_width=True, key=f"pnl_chart_{time.time()}")

                closed_trades['week'] = closed_trades['timestamp'].dt.isocalendar().week
                weekly_stats = closed_trades.groupby('week')['pnl'].sum().reset_index()

                fig2 = px.bar(
                    weekly_stats,
                    x='week',
                    y='pnl',
                    title="Συνολικό PnL Ανά Εβδομάδα",
                    template="plotly_dark",
                    color_discrete_sequence=["#00FF00"],
                )
                st.plotly_chart(fig2, use_container_width=True, key=f"weekly_chart_{time.time()}")

            st.markdown('<div class="glow-line"></div>', unsafe_allow_html=True)

            st.info(f"⏱️ Τελευταία ενημέρωση: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Ανανεώνεται κάθε {REFRESH_INTERVAL} δευτερόλεπτα.")

        except Exception as e:
            st.error(f"❌ Σφάλμα κατά την ανάγνωση του αρχείου: {e}")

        time.sleep(REFRESH_INTERVAL)
