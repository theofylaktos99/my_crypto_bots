# 🚀 Quick Deployment Reference

This is a quick reference guide for deploying CryptoBot Dashboard. For detailed instructions, see [DEPLOYMENT.md](DEPLOYMENT.md).

## 📦 Prerequisites

```bash
# 1. Ensure you have Python 3.9+
python3 --version

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 4. Run locally
streamlit run src/dashboard/flynt_style_dashboard.py
```

---

## ☁️ Deploy to Streamlit Cloud (Fastest - 5 minutes)

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Go to [share.streamlit.io](https://share.streamlit.io)**

3. **New app:**
   - Repository: `theofylaktos99/my_crypto_bots`
   - Branch: `main`
   - Main file: `src/dashboard/flynt_style_dashboard.py`

4. **Add secrets** (in Advanced settings):
   ```toml
   [binance]
   api_key = "your_api_key"
   api_secret = "your_api_secret"
   sandbox_mode = true
   ```

5. **Click Deploy!** ✨

**Your app will be live at:** `https://your-app-name.streamlit.app`

---

## 🔷 Deploy to Heroku (10 minutes)

```bash
# 1. Install Heroku CLI
# See: https://devcenter.heroku.com/articles/heroku-cli

# 2. Login
heroku login

# 3. Create app
heroku create my-crypto-bot

# 4. Set environment variables
heroku config:set API_KEY=your_key
heroku config:set SECRET_KEY=your_secret
heroku config:set USE_TESTNET=true

# 5. Deploy
git push heroku main

# 6. Open app
heroku open
```

---

## 🚂 Deploy to Railway (5 minutes)

1. **Go to [railway.app](https://railway.app)**
2. **New Project → Deploy from GitHub**
3. **Select repository:** `my_crypto_bots`
4. **Add variables** in Variables tab:
   ```
   API_KEY=your_key
   SECRET_KEY=your_secret
   USE_TESTNET=true
   PORT=8501
   ```
5. **Set start command** in Settings:
   ```
   streamlit run src/dashboard/flynt_style_dashboard.py --server.port=$PORT --server.address=0.0.0.0
   ```
6. **Deploy!** 🎉

---

## 🐳 Deploy with Docker (Anywhere)

```bash
# 1. Build image
docker build -t cryptobot .

# 2. Run container
docker run -d \
  -p 8501:8501 \
  -e API_KEY=your_key \
  -e SECRET_KEY=your_secret \
  -e USE_TESTNET=true \
  --name cryptobot-dashboard \
  cryptobot

# 3. Access at http://localhost:8501

# Or use docker-compose
docker-compose up -d
```

---

## 🔐 Security Checklist

Before deploying to production:

- [ ] Use testnet API keys for testing
- [ ] Never commit `.env` or `secrets.toml` to git
- [ ] Enable 2FA on exchange accounts
- [ ] Use read-only API keys if only viewing data
- [ ] Set appropriate API permissions
- [ ] Review `.gitignore` to ensure secrets are excluded
- [ ] Use environment variables for all sensitive data
- [ ] Enable HTTPS (automatic on most platforms)
- [ ] Set strong passwords for any dashboards
- [ ] Regularly rotate API keys
- [ ] Monitor API usage and rate limits

---

## 🧪 Testing Before Deployment

```bash
# 1. Run syntax checks
python3 -m py_compile src/dashboard/flynt_style_dashboard.py

# 2. Test locally
./start.sh  # Linux/Mac
start.bat   # Windows

# 3. Check for security issues (optional)
pip install bandit
bandit -r src/

# 4. Run tests (if available)
pytest tests/
```

---

## 📊 Post-Deployment

After deployment:

1. **Test the app thoroughly**
2. **Monitor logs** for errors
3. **Check API rate limits**
4. **Set up alerts** for important events
5. **Document your deployment** process
6. **Share with team** (if applicable)

---

## 🆘 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| App won't start | Check logs, verify dependencies |
| API errors | Verify keys, check testnet mode |
| Import errors | Update requirements.txt |
| Slow performance | Enable caching, optimize queries |
| Memory issues | Upgrade instance, reduce data retention |

For detailed troubleshooting, see [DEPLOYMENT.md](DEPLOYMENT.md#troubleshooting)

---

## 📚 Resources

- [Streamlit Docs](https://docs.streamlit.io)
- [Heroku Python Guide](https://devcenter.heroku.com/categories/python-support)
- [Railway Docs](https://docs.railway.app)
- [Docker Docs](https://docs.docker.com)
- [Binance API](https://binance-docs.github.io/apidocs/)

---

## 💡 Pro Tips

- Start with Streamlit Cloud (easiest)
- Use testnet first, always
- Monitor your deployments
- Keep dependencies updated
- Automate with GitHub Actions
- Use Docker for consistency
- Document your setup

---

**Need help?** Open an issue on GitHub or check [DEPLOYMENT.md](DEPLOYMENT.md)

**Ready to deploy?** Choose your platform above and follow the steps! 🚀
