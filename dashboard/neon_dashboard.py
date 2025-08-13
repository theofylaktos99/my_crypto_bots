import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import time
import os

# === Ρυθμίσεις ===
LOG_FILE_PATH = r"c:\DEV PORTOFOLIO\my_crypto_bots\test_data_clean.csv"
REFRESH_INTERVAL = 10  # δευτερόλεπτα

# === Αρχικοποίηση Streamlit ===
st.set_page_config(page_title="Neon Bot Dashboard", layout="wide")

# === Custom Cyberpunk Style (CSS + animation) ===
st.markdown("""
<style>
/* Animated Neon Gradient Background */
body {
  background: linear-gradient(-45deg, #0f0c29, #302b63, #24243e, #1a1a2e);
  background-size: 400% 400%;
  animation: gradientMove 15s ease infinite;
  color: #ffffff;
}

@keyframes gradientMove {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

h1, h2, h3 {
  color: #ff00ff;
  text-shadow: 0 0 5px #ff00ff, 0 0 10px #ff00ff;
}

.stMetric {
  background-color: #111111aa !important;
  border: 1px solid #ff00ff55 !important;
  border-radius: 10px;
  padding: 10px;
  color: white;
  text-shadow: 0 0 5px #00ffff;
}

[data-testid="stMetricValue"] {
  font-weight: bold;
  color: #00ffff !important;
}

.block-container {
  padding-top: 2rem;
}

.stDataFrame th, .stDataFrame td {
  background-color: #1a1a2e !important;
  color: white !important;
}
</style>
""", unsafe_allow_html=True)

# === Τίτλος Dashboard ===
st.title("💡 Neon RSI Bot Dashboard")

# === Ζώνη Επαναλαμβανόμενης Ανανέωσης ===
with st.empty():
    while True:
        try:
            # === Ανάγνωση και Προετοιμασία Δεδομένων ===
            df = pd.read_csv(LOG_FILE_PATH)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df.sort_values('timestamp', inplace=True)

            closed_trades = df[df['action'].str.contains("SELL")].copy()
            wins = closed_trades[closed_trades['pnl'] > 0]
            avg_pnl_pct = closed_trades['pnl_percent'].mean() if not closed_trades.empty else 0.0
            winrate = (len(wins) / len(closed_trades)) * 100 if not closed_trades.empty else 0.0

            # === Ενότητες Απόδοσης ===
            st.markdown("## 🔮 Απόδοση")
            col1, col2, col3 = st.columns(3)
            col1.metric("Κλειστά Trades", len(closed_trades))
            col2.metric("Win Rate", f"{winrate:.2f}%")
            col3.metric("Μέσο PnL %", f"{avg_pnl_pct:.2f}%")

            # === Τελευταία Trades ===
            st.markdown("---")
            st.markdown("## 📋 Πρόσφατα Trades")
            st.dataframe(df.tail(15), use_container_width=True)

            # === Γραφήματα ===
            st.markdown("---")
            st.markdown("## 📈 Γραφήματα Απόδοσης")
            if not closed_trades.empty:
                fig1 = px.line(closed_trades, x='timestamp', y='pnl',
                               title="PnL ανά Trade", markers=True,
                               template="plotly_dark", line_shape="spline")
                st.plotly_chart(fig1, use_container_width=True, key="pnl_line_chart")

                closed_trades['week'] = closed_trades['timestamp'].dt.isocalendar().week
                weekly_stats = closed_trades.groupby('week')['pnl'].sum().reset_index()
                fig2 = px.bar(weekly_stats, x='week', y='pnl',
                              title="Συνολικό PnL ανά Εβδομάδα", template="plotly_dark",
                              color_discrete_sequence=["#ff00ff"])
                st.plotly_chart(fig2, use_container_width=True, key="weekly_bar_chart")

            # === Χρονική Ενημέρωση UI ===
            st.markdown("---")
            st.info(f"🕒 Τελευταία ενημέρωση: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        except Exception as e:
            st.error(f"❌ Σφάλμα κατά την ανάγνωση του αρχείου: {e}")

        time.sleep(REFRESH_INTERVAL)