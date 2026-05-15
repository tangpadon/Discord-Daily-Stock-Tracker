import sys

sys.stdout.reconfigure(encoding='utf-8')

import yfinance as yf
import json
import os
import requests
from dotenv import load_dotenv

load_dotenv(override=True)
WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
PORTFOLIO_FILE = "portfolio.json"

def load_portfolio():
    if not os.path.exists(PORTFOLIO_FILE):
        return []
    with open(PORTFOLIO_FILE, "r") as f:
        data = json.load(f)
        return data.get("portfolio", [])

def check_portfolio():
    portfolio = load_portfolio()
    if not portfolio:
        print("🤷‍♂️ No stocks found in portfolio.")
        return

    fields = []
    
    print("🔍 Starting portfolio check...")

    for item in portfolio:
        symbol = item['ticker']
        avg_cost = item['avg_price']
        
        try:
            # Fetch current price (yfinance)
            ticker = yf.Ticker(symbol)
            current_price = ticker.fast_info['lastPrice']
            
            diff_percent = ((current_price - avg_cost) / avg_cost) * 100
            
            # Logic for "Average Down" Opportunity พร้อมใส่อิโมจิ
            status_text = "N/A"
            if diff_percent <= -10.0:
                status_text = "🚨 GOOD OPPORTUNITY TO AVERAGE DOWN 🚨"
            elif diff_percent < 0:
                status_text = "📉 Below Cost"
            else:
                status_text = "📈 In Profit"

            fields.append({
                "name": f"🏢 Stock: {symbol}",
                "value": f"Current: ${current_price:.2f} | Avg: ${avg_cost:.2f}\nChange: **{diff_percent:.2f}%**\nStatus: {status_text}",
                "inline": False
            })
            
        except Exception as e:
            print(f"❌ Error fetching {symbol}: {e}")
            fields.append({
                "name": f"⚠️ Stock: {symbol}",
                "value": "Error fetching data. Check ticker symbol.",
                "inline": False
            })

    # Prepare Discord Payload พร้อมใส่อิโมจิที่หัวข้อ
    payload = {
        "embeds": [{
            "title": "📊 Daily Portfolio Status Report",
            "color": 3447003, # Blue
            "fields": fields,
            "footer": {"text": "Stock data from Yahoo Finance"}
        }]
    }

    if WEBHOOK_URL:
        requests.post(WEBHOOK_URL, json=payload)
        print("✅ Daily report sent to Discord.")
    else:
        print("⚠️ Warning: DISCORD_WEBHOOK_URL is missing.")

if __name__ == "__main__":
    check_portfolio()