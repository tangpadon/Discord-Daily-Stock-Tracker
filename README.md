# 📊 Daily Portfolio Tracker & Average-Down Notifier

An automated Python-based stock portfolio monitor that sends daily status reports and "Average Down" alerts directly to your Discord channel. Designed to run 100% free using GitHub Actions while keeping your stock holdings completely private using GitHub Gist.

---

## ✨ Features
- **🔒 100% Private Holdings:** Keeps your portfolio secret using GitHub Gist so your holdings and quantities are never exposed in public Git repositories.
- **Daily Reports:** Automated summary of your portfolio performance sent after market close.
- **Dip Detection:** Special alerts when a stock's price drops significantly below your average cost (Default: -10%).
- **Real-time Data:** Uses `yfinance` to fetch the latest market prices (US Markets).
- **Visual Alerts:** Clean Discord Embed messages with emojis and formatted data for easy reading.
- **No Server Required:** Fully automated using GitHub Actions (Cron schedule).
- **PEP 8 Compliant:** Clean, modular, type-annotated Python codebase.

---

## 🛠️ Prerequisites
- A **Discord Server** and a **Webhook URL**.
- A **GitHub Account** (to host the code and run the automation).
- (Optional) Python 3.10+ installed on your local machine for testing.

---

## 🚀 Setup Instructions

### 1. Fork this Repository
Click the **Fork** button at the top right of this page to create a copy of this project under your own account.

---

### 2. Create Your Secret Portfolio on GitHub Gist (Privacy-Safe)

To prevent revealing your stock holdings in a public repository, store your portfolio in a **Secret GitHub Gist**:

1. Go to [gist.github.com](https://gist.github.com).
2. Set the file name to `portfolio.json`.
3. Paste your stock holdings in JSON format:
   ```json
   {
     "portfolio": [
       {"ticker": "AAPL", "avg_price": 170.50, "quantity": 10},
       {"ticker": "NVDA", "avg_price": 120.00, "quantity": 5},
       {"ticker": "BRK-B", "avg_price": 400.00, "quantity": 12}
     ]
   }
   ```
   *Note: For tickers with dots (e.g. `BRK.B`), use a hyphen instead (`BRK-B`) for Yahoo Finance compatibility.*
4. Click the dropdown arrow on the create button and select **"Create secret gist"**.
5. Click the **"Raw"** button on the top right of your newly created Gist, and copy the browser URL.
   - Example URL: `https://gist.githubusercontent.com/<username>/<gist_id>/raw/portfolio.json`

---

### 3. Setup Discord Webhook
1. In your Discord server, go to **Server Settings > Integrations > Webhooks**.
2. Click **New Webhook** and copy the **Webhook URL**.

---

### 4. Configure GitHub Repository Secrets

In your GitHub repository:
1. Go to **Settings > Secrets and variables > Actions**.
2. Click **New repository secret** and add the following:

| Secret Name | Description | Example / Required |
| :--- | :--- | :--- |
| `DISCORD_WEBHOOK_URL` | Your Discord Webhook URL | Required |
| `PORTFOLIO_GIST_URL` | The Raw URL of your secret Gist | Required (or use `GIST_ID`) |
| `GIST_ID` | Gist ID (alternative to URL) | Optional |
| `GIST_TOKEN` | GitHub Personal Access Token (for private API access) | Optional |

---

### 5. Enable Automation
1. Go to the **Actions** tab in your repository.
2. Click the button to enable workflows if prompted.
3. The bot is scheduled to run every Monday–Friday at 21:30 UTC (after US market close).
4. You can also trigger it manually at any time by selecting **Daily Portfolio Monitor** workflow and clicking **Run workflow**.

---

## 💻 Local Development & Testing

1. Clone your repository:
   ```bash
   git clone https://github.com/<your-username>/Discord-Daily-Stock-Tracker.git
   cd Discord-Daily-Stock-Tracker
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root:
   ```env
   DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/..."
   PORTFOLIO_GIST_URL="https://gist.githubusercontent.com/..."
   ```

   *Alternatively, for offline local testing, you can create a local `portfolio.json` (which is ignored by Git in `.gitignore`):*
   ```bash
   cp portfolio.example.json portfolio.json
   ```

4. Run the tracker:
   ```bash
   python main.py
   ```

---

## 📜 Code Quality & Standards

This project adheres strictly to **PEP 8** style guidelines:
- Fully type-annotated (`typing`)
- Verified with `flake8`
- Error-tolerant ticker queries (prevents individual ticker failures from aborting the run)
- Network request timeouts configured
