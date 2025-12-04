# 🤖 Professional Crypto Trading Bot System

## 📋 TABLE OF CONTENTS

1. [System Overview](#system-overview)
2. [Quick Start Guide](#quick-start-guide)
3. [Project Structure](#project-structure)
4. [Component Documentation](#component-documentation)
5. [Configuration Guide](#configuration-guide)
6. [Safety & Security](#safety-security)
7. [Troubleshooting](#troubleshooting)
8. [API Reference](#api-reference)
9. [Performance Optimization](#performance-optimization)
10. [Advanced Features](#advanced-features)
11. [FAQ](#faq)
12. [Support & Community](#support-community)
13. [Changelog & Updates](#changelog--updates)

---

## 🎯 SYSTEM OVERVIEW

### Modern Modular Architecture

```
my_crypto_bots/
├── .env, .env.example
├── requirements.txt
├── README.md
├── src/
│   ├── api/           # Exchange & data integrations
│   ├── bots/          # Bot implementations
│   ├── dashboard/     # Main dashboard (Streamlit)
│   ├── strategies/    # Trading strategies
│   └── utils/         # Utilities, config, error handling
├── config/            # YAML/JSON config files
├── logs/              # Log files
├── backups/           # Backups
├── old/               # Legacy code & dashboards
└── venv_new/, zscore_env/  # Python environments
```

- **Main Dashboard Entry Point:** `src/dashboard/flynt_style_dashboard.py`
- **All legacy dashboards/scripts:** `old/`
- **All new code:** `src/`

---

## 🚀 QUICK START GUIDE

### 1. Clone & Setup
```bash
git clone https://github.com/theofylaktos99/my_crypto_bots.git
cd my_crypto_bots
python -m venv venv_new
venv_new\Scripts\activate  # (Windows)
pip install -r requirements.txt
```

### 2. Configure Environment
- Copy `.env.example` to `.env` and fill in your API keys and settings:
```bash
cp .env.example .env
# Edit .env with your favorite editor
```

### 3. Launch the Dashboard
```bash
streamlit run src/dashboard/flynt_style_dashboard.py
```
- Access at: http://localhost:8501

### 4. Deploy to Cloud (Optional)
For detailed deployment instructions, see **[DEPLOYMENT.md](DEPLOYMENT.md)**

**Quick Deploy Options:**
- 🟢 **Streamlit Cloud** (Recommended - Free): [share.streamlit.io](https://share.streamlit.io)
- 🔵 **Heroku**: See [DEPLOYMENT.md](DEPLOYMENT.md#heroku-deployment)
- 🚂 **Railway**: See [DEPLOYMENT.md](DEPLOYMENT.md#railway-deployment)
- 🐳 **Docker**: See [DEPLOYMENT.md](DEPLOYMENT.md#docker-deployment)

---

## 🗂️ PROJECT STRUCTURE

See also `CURRENT_STRUCTURE.md` for a live snapshot.

- `src/dashboard/flynt_style_dashboard.py` — Main Streamlit dashboard (FLYNT UI)
- `src/` — All new modular code (api, bots, strategies, utils)
- `old/` — All legacy dashboards, scripts, and experiments
- `config/`, `logs/`, `backups/` — Supporting files
- `.env`, `requirements.txt`, `README.md` — Project config & docs

---

## 🔧 COMPONENT DOCUMENTATION

- **Trading Engine:** `src/bots/live_trading_bot.py`
- **Portfolio Manager:** `src/utils/portfolio_manager.py`
- **Configuration Manager:** `src/utils/config_manager.py`
- **Error Handler:** `src/utils/error_handler.py`
- **Bot Integration:** `src/bots/bot_integration.py`
- **Main Dashboard:** `src/dashboard/flynt_style_dashboard.py`

(Για λεπτομέρειες, δες τα docstrings σε κάθε αρχείο ή το αναλυτικό documentation παραπάνω)

---

## ⚙️ CONFIGURATION GUIDE

- Όλες οι ρυθμίσεις στο `.env` και στα αρχεία του `config/`
- Κάθε strategy και bot έχει παραμετροποίηση μέσω YAML/ENV ή UI

---

## 🔐 SAFETY & SECURITY

- Όλα τα API keys στο `.env` (ποτέ στο Git!)
- Υποστήριξη testnet/mainnet
- Risk management σε επίπεδο στρατηγικής και portfolio

---

## 🚀 DEPLOYMENT & CI/CD

### Cloud Deployment Options

The application is now ready for deployment to multiple cloud platforms:

- **Streamlit Cloud**: Zero-config deployment with automatic updates
- **Heroku**: Scalable PaaS with extensive add-ons
- **Railway**: Modern platform with generous free tier
- **Docker**: Container-based deployment for any platform

See **[DEPLOYMENT.md](DEPLOYMENT.md)** for detailed instructions.

### Continuous Integration

GitHub Actions workflows are configured for:
- ✅ Automated testing across Python 3.9, 3.10, 3.11
- ✅ Code quality checks (flake8, black, pylint)
- ✅ Security scanning (bandit, safety)
- ✅ Code complexity analysis

### Configuration Files

- `.streamlit/config.toml` - Streamlit configuration
- `.streamlit/secrets.toml.example` - Secrets template
- `.env.example` - Environment variables template
- `Dockerfile` - Docker container configuration
- `docker-compose.yml` - Docker Compose orchestration
- `Procfile` - Heroku deployment configuration
- `.github/workflows/ci.yml` - CI/CD pipeline

---

## 🛠️ DEVELOPMENT & EXTENSION

- **Νέες στρατηγικές:** Πρόσθεσε αρχεία στο `src/strategies/`
- **Νέοι bots:** Πρόσθεσε στο `src/bots/`
- **Νέες σελίδες dashboard:** Πρόσθεσε στο `src/dashboard/`

---

## 🏁 CONCLUSION

Το σύστημα είναι πλήρως οργανωμένο, modular, και έτοιμο για παραγωγή ή επέκταση. Όλη η legacy λογική έχει αρχειοθετηθεί, το documentation είναι πλήρες, και το entry point είναι το `src/dashboard/flynt_style_dashboard.py`.

**Για ερωτήσεις, υποστήριξη ή προτάσεις, άνοιξε issue στο GitHub repo!**

---

*Για πλήρη τεχνική τεκμηρίωση, παραδείγματα χρήσης και troubleshooting, δες τα sections παραπάνω ή το `CURRENT_STRUCTURE.md`.*
