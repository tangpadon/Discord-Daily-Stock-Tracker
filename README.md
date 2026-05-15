# 📊 Daily Portfolio Tracker & Average-Down Notifier

An automated Python-based stock portfolio monitor that sends daily status reports and "Average Down" alerts directly to your Discord channel. Designed to run 100% free using GitHub Actions.

## ✨ Features
- **Daily Reports:** Automated summary of your portfolio performance sent after market close.
- **Dip Detection:** Special alerts when a stock's price drops significantly below your average cost (Default: -10%).
- **Real-time Data:** Uses `yfinance` to fetch the latest market prices (US Markets).
- **Visual Alerts:** Clean Discord Embed messages with emojis and formatted data for easy reading.
- **No Server Required:** Fully automated using GitHub Actions (Cron schedule).

---

## 🛠️ Prerequisites
- A **Discord Server** and a **Webhook URL**.
- A **GitHub Account** (to host the code and run the automation).
- (Optional) Python 3.10+ installed on your local machine for testing.

---

## 🚀 Setup Instructions

### 1. Fork this Repository
Click the **Fork** button at the top right of this page to create a copy of this project under your own account.

### 2. Configure Your Portfolio
1. Open the `portfolio.json` file in your repository.
2. Edit the file with your actual stock holdings:
   ```json
   {
     "portfolio": [
       {"ticker": "AAPL", "avg_price": 170.50, "quantity": 10},
       {"ticker": "NVDA", "avg_price": 850.00, "quantity": 5},
       {"ticker": "BRK-B", "avg_price": 400.00, "quantity": 12}
     ]
   }

*Note: For symbols with dots (like BRK.B), use a hyphen instead (BRK-B) for Yahoo Finance compatibility.*

### 3. Setup Discord Webhook
1. In your Discord server, go to Channel Settings > Integrations > Webhooks.

2. Create a new Webhook and copy the Webhook URL.

3. In your GitHub repository, go to Settings > Secrets and variables > Actions.

4. Click New repository secret.

   Name: DISCORD_WEBHOOK_URL

   Secret: Paste your Webhook URL here. (Make sure there are no quotes or spaces).

### 4. Enable Automation
1. Go to the Actions tab in your repository.

2. Click the button to enable workflows if prompted.

3. The bot is scheduled to run every Monday-Friday at 21:00 UTC (after US market close).

4. You can also trigger it manually by selecting the Daily Portfolio Monitor workflow and clicking Run workflow.

---
