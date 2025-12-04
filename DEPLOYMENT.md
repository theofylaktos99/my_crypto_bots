# 🚀 Deployment Guide for CryptoBot Dashboard

This guide provides comprehensive instructions for deploying the CryptoBot trading dashboard to various cloud platforms.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Streamlit Cloud Deployment](#streamlit-cloud-deployment)
3. [Heroku Deployment](#heroku-deployment)
4. [Railway Deployment](#railway-deployment)
5. [Docker Deployment](#docker-deployment)
6. [Environment Configuration](#environment-configuration)
7. [Troubleshooting](#troubleshooting)

---

## 🔧 Prerequisites

Before deploying, ensure you have:

- ✅ A GitHub account with this repository
- ✅ Binance API keys (testnet or mainnet)
- ✅ Python 3.9+ installed locally for testing
- ✅ Git installed and configured
- ✅ Required dependencies installed: `pip install -r requirements.txt`

---

## ☁️ Streamlit Cloud Deployment

**Streamlit Cloud** is the easiest way to deploy your Streamlit app. It's free for public repositories!

### Step 1: Prepare Your Repository

1. Ensure your repository is pushed to GitHub
2. Make sure all required files are present:
   - `requirements.txt`
   - `.streamlit/config.toml`
   - `src/dashboard/flynt_style_dashboard.py`

### Step 2: Deploy to Streamlit Cloud

1. **Go to [share.streamlit.io](https://share.streamlit.io)**

2. **Sign in** with your GitHub account

3. **Click "New app"**

4. **Configure your app:**
   - **Repository:** `theofylaktos99/my_crypto_bots`
   - **Branch:** `main` (or your preferred branch)
   - **Main file path:** `src/dashboard/flynt_style_dashboard.py`

5. **Click "Advanced settings"** and add your secrets:

```toml
# In the Secrets section, add:
[binance]
api_key = "your_binance_api_key"
api_secret = "your_binance_api_secret"
sandbox_mode = true

[app]
environment = "production"
debug_mode = false
```

6. **Click "Deploy"** and wait for the app to build (2-5 minutes)

7. **Your app is now live!** Share the URL with others.

### Step 3: Update Your Deployment

- Any push to your selected branch will automatically trigger a redeploy
- You can manually trigger a reboot from the Streamlit Cloud dashboard
- Update secrets in the app settings without redeploying

### Streamlit Cloud Features

- ✅ **Free tier:** Unlimited public apps
- ✅ **Automatic updates:** Redeploys on git push
- ✅ **Built-in secrets management**
- ✅ **Custom domains** (paid plans)
- ✅ **SSL/HTTPS** included
- ✅ **Monitoring and logs**

---

## 🔷 Heroku Deployment

**Heroku** is a popular PaaS that supports Python applications.

### Step 1: Install Heroku CLI

```bash
# macOS
brew tap heroku/brew && brew install heroku

# Windows (with Chocolatey)
choco install heroku-cli

# Linux
curl https://cli-assets.heroku.com/install.sh | sh
```

### Step 2: Create Required Files

Create a `Procfile` in the root directory:

```bash
echo "web: streamlit run src/dashboard/flynt_style_dashboard.py --server.port=\$PORT --server.address=0.0.0.0" > Procfile
```

Create a `runtime.txt`:

```bash
echo "python-3.11.0" > runtime.txt
```

### Step 3: Deploy to Heroku

```bash
# Login to Heroku
heroku login

# Create a new Heroku app
heroku create my-crypto-bot-dashboard

# Set environment variables
heroku config:set API_KEY=your_binance_api_key
heroku config:set SECRET_KEY=your_binance_api_secret
heroku config:set USE_TESTNET=true

# Deploy
git push heroku main

# Open your app
heroku open

# View logs
heroku logs --tail
```

### Heroku Configuration

- **Dyno size:** Start with `hobby` ($7/month) or `free` (limited hours)
- **Add-ons:** Consider Redis for caching or Postgres for data storage
- **Custom domain:** Available on all paid plans

---

## 🚂 Railway Deployment

**Railway** is a modern platform with a generous free tier and excellent developer experience.

### Step 1: Sign Up

1. Go to [railway.app](https://railway.app)
2. Sign in with GitHub

### Step 2: Deploy from GitHub

1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Choose your `my_crypto_bots` repository
4. Railway will auto-detect it as a Python app

### Step 3: Configure Environment

1. Go to **Variables** tab
2. Add your environment variables:

```
API_KEY=your_binance_api_key
SECRET_KEY=your_binance_api_secret
USE_TESTNET=true
PORT=8501
```

### Step 4: Configure Start Command

1. Go to **Settings** tab
2. Set **Start Command:**

```bash
streamlit run src/dashboard/flynt_style_dashboard.py --server.port=$PORT --server.address=0.0.0.0
```

3. Click **Deploy**

### Railway Features

- ✅ **$5 free credit per month**
- ✅ **Automatic HTTPS**
- ✅ **Custom domains**
- ✅ **Zero-config deployments**
- ✅ **Built-in monitoring**

---

## 🐳 Docker Deployment

**Docker** allows you to containerize your application for consistent deployment anywhere.

### Step 1: Create Dockerfile

Create a `Dockerfile` in the root directory:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run the application
CMD ["streamlit", "run", "src/dashboard/flynt_style_dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Step 2: Create docker-compose.yml

```yaml
version: '3.8'

services:
  cryptobot:
    build: .
    ports:
      - "8501:8501"
    environment:
      - API_KEY=${API_KEY}
      - SECRET_KEY=${SECRET_KEY}
      - USE_TESTNET=true
    volumes:
      - ./logs:/app/logs
      - ./config:/app/config
    restart: unless-stopped
```

### Step 3: Build and Run

```bash
# Build the image
docker build -t cryptobot-dashboard .

# Run the container
docker run -p 8501:8501 \
  -e API_KEY=your_api_key \
  -e SECRET_KEY=your_secret_key \
  -e USE_TESTNET=true \
  cryptobot-dashboard

# Or use docker-compose
docker-compose up -d

# View logs
docker logs -f cryptobot
```

### Deploy to Cloud with Docker

**Deploy to AWS ECS, Google Cloud Run, or Azure Container Instances:**

```bash
# Tag your image
docker tag cryptobot-dashboard your-registry/cryptobot-dashboard

# Push to registry
docker push your-registry/cryptobot-dashboard

# Deploy to your cloud provider
```

---

## ⚙️ Environment Configuration

### Required Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `API_KEY` | Binance API key | `abc123...` |
| `SECRET_KEY` | Binance API secret | `xyz789...` |
| `USE_TESTNET` | Use testnet (true) or mainnet (false) | `true` |
| `ENVIRONMENT` | Environment name | `production` |

### Optional Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG_MODE` | Enable debug logging | `false` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `DEFAULT_SYMBOL` | Default trading pair | `BTC/USDT` |
| `DEFAULT_TIMEFRAME` | Default timeframe | `1h` |
| `MAX_CONCURRENT_BOTS` | Max concurrent bots | `5` |

### Setting Environment Variables

**Streamlit Cloud:**
- Use the Secrets management in app settings
- Format as TOML

**Heroku:**
```bash
heroku config:set VAR_NAME=value
```

**Railway:**
- Use the Variables tab in the dashboard

**Docker:**
```bash
docker run -e VAR_NAME=value ...
```

---

## 🔍 Troubleshooting

### Common Issues

#### 1. **App won't start**

**Problem:** The app crashes on startup

**Solutions:**
- Check that all dependencies are installed
- Verify Python version (3.9+)
- Check logs for specific error messages
- Ensure all config files are present

#### 2. **API Connection Errors**

**Problem:** Cannot connect to Binance API

**Solutions:**
- Verify API keys are correct
- Check if you're using testnet keys with testnet mode
- Ensure API keys have correct permissions
- Check network/firewall settings

#### 3. **Import Errors**

**Problem:** Module not found errors

**Solutions:**
- Ensure `requirements.txt` is up to date
- Run `pip install -r requirements.txt`
- Check Python version compatibility
- Clear pip cache: `pip cache purge`

#### 4. **Memory Issues**

**Problem:** App runs out of memory

**Solutions:**
- Reduce data retention period in config
- Optimize data caching
- Upgrade to a larger dyno/instance
- Implement database storage for historical data

#### 5. **Slow Performance**

**Problem:** Dashboard is slow or unresponsive

**Solutions:**
- Enable caching in Streamlit
- Reduce data refresh frequency
- Optimize database queries
- Use asynchronous API calls
- Consider a CDN for static assets

### Getting Help

- 📖 **Documentation:** Check the main README.md
- 🐛 **Issues:** Open an issue on GitHub
- 💬 **Community:** Join discussions in GitHub Discussions
- 📧 **Support:** Contact through GitHub

---

## 🎯 Best Practices

### Security

- ✅ Never commit API keys to version control
- ✅ Use environment variables or secrets management
- ✅ Enable 2FA on exchange accounts
- ✅ Use testnet for development
- ✅ Regularly rotate API keys
- ✅ Set appropriate API permissions (read-only for viewing)

### Performance

- ✅ Enable caching for expensive operations
- ✅ Use connection pooling for databases
- ✅ Implement rate limiting for API calls
- ✅ Monitor resource usage
- ✅ Set up alerts for errors

### Monitoring

- ✅ Set up logging aggregation
- ✅ Monitor API rate limits
- ✅ Track application errors
- ✅ Monitor trading performance
- ✅ Set up health checks

---

## 🚀 Next Steps

After deployment:

1. **Test thoroughly** with testnet before going live
2. **Monitor performance** and adjust settings
3. **Set up backups** for configuration and data
4. **Configure alerts** for important events
5. **Document** your deployment process
6. **Review security** settings regularly

---

## 📚 Additional Resources

- [Streamlit Documentation](https://docs.streamlit.io)
- [Heroku Python Guide](https://devcenter.heroku.com/articles/getting-started-with-python)
- [Railway Documentation](https://docs.railway.app)
- [Docker Documentation](https://docs.docker.com)
- [Binance API Documentation](https://binance-docs.github.io/apidocs/)
- [CCXT Documentation](https://docs.ccxt.com/)

---

**💡 Tip:** Always test your deployment on testnet first before connecting to mainnet with real funds!

**⚠️ Warning:** Trading cryptocurrency involves risk. Never trade with money you can't afford to lose.

---

*Last Updated: December 2025*
