"""Daily Stock Portfolio Tracker & Discord Alert Notifier.

Fetches stock prices using Yahoo Finance (yfinance) and sends daily status
reports and "Average Down" notifications to a Discord webhook. Supports
loading portfolio data securely from a private GitHub Gist or local JSON.
"""

import json
import os
import sys
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from dotenv import load_dotenv
import requests
import yfinance as yf

# Configure UTF-8 encoding for standard output (e.g. Windows terminal)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

load_dotenv(override=True)

# Configuration & Environment Variables
WEBHOOK_URL: Optional[str] = os.environ.get("DISCORD_WEBHOOK_URL")
PORTFOLIO_GIST_URL: Optional[str] = os.environ.get("PORTFOLIO_GIST_URL")
GIST_ID: Optional[str] = os.environ.get("GIST_ID")
GIST_TOKEN: Optional[str] = os.environ.get("GIST_TOKEN") or os.environ.get(
    "GITHUB_TOKEN"
)
DEFAULT_PORTFOLIO_FILE: str = os.environ.get(
    "PORTFOLIO_FILE", "portfolio.json"
)

# Constants
HTTP_TIMEOUT: int = 15
DEFAULT_EMBED_COLOR: int = 3447003  # Discord Blue
DIP_THRESHOLD_PERCENT: float = -10.0


def _build_auth_headers(token: Optional[str]) -> Dict[str, str]:
    """Build HTTP headers with authorization if token is provided."""
    headers: Dict[str, str] = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Discord-Daily-Stock-Tracker",
    }
    if token and token.strip():
        headers["Authorization"] = f"Bearer {token.strip()}"
    return headers


def _extract_gist_id_from_url(url: str) -> Optional[str]:
    """Extract Gist ID from a GitHub Gist web URL if applicable."""
    parsed = urlparse(url)
    if parsed.netloc == "gist.github.com":
        parts = [p for p in parsed.path.strip("/").split("/") if p]
        if parts:
            return parts[-1]
    return None


def fetch_portfolio_from_gist_api(
    gist_id: str,
    token: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Fetch and parse portfolio data from GitHub Gist REST API."""
    api_url = f"https://api.github.com/gists/{gist_id}"
    headers = _build_auth_headers(token)

    try:
        response = requests.get(api_url, headers=headers, timeout=HTTP_TIMEOUT)
        response.raise_for_status()
        gist_data = response.json()
        files = gist_data.get("files", {})

        if not files:
            print(f"⚠️ Gist {gist_id} contains no files.")
            return []

        # Look for portfolio.json or the first .json file or the first file
        target_file = files.get("portfolio.json")
        if not target_file:
            for filename, file_obj in files.items():
                if filename.lower().endswith(".json"):
                    target_file = file_obj
                    break
        if not target_file:
            target_file = next(iter(files.values()))

        # If file content is truncated, fetch via raw_url
        if target_file.get("truncated") and target_file.get("raw_url"):
            raw_url = target_file["raw_url"]
            raw_resp = requests.get(
                raw_url, headers=headers, timeout=HTTP_TIMEOUT
            )
            raw_resp.raise_for_status()
            data = raw_resp.json()
        else:
            raw_content = target_file.get("content", "{}")
            data = json.loads(raw_content)

        if isinstance(data, dict):
            return data.get("portfolio", [])
        if isinstance(data, list):
            return data
        return []

    except requests.RequestException as err:
        print(f"❌ Failed to fetch Gist via API ({gist_id}): {err}")
        return []
    except json.JSONDecodeError as err:
        print(f"❌ Failed to parse JSON from Gist ({gist_id}): {err}")
        return []


def fetch_portfolio_from_url(
    url: str,
    token: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Fetch portfolio data from a raw URL or direct Gist link."""
    # Check if this is a standard gist.github.com web page URL
    extracted_id = _extract_gist_id_from_url(url)
    if extracted_id:
        return fetch_portfolio_from_gist_api(extracted_id, token=token)

    headers = _build_auth_headers(token)
    try:
        response = requests.get(url, headers=headers, timeout=HTTP_TIMEOUT)
        response.raise_for_status()
        data = response.json()

        # Handle GitHub API response if user provided an api.github.com URL
        if isinstance(data, dict) and "files" in data:
            files = data.get("files", {})
            target_file = files.get("portfolio.json") or next(
                iter(files.values()), {}
            )
            content = target_file.get("content", "{}")
            data = json.loads(content)

        if isinstance(data, dict):
            return data.get("portfolio", [])
        if isinstance(data, list):
            return data
        return []

    except requests.RequestException as err:
        print(f"❌ Failed to fetch portfolio from URL: {err}")
        return []
    except json.JSONDecodeError as err:
        print(f"❌ Failed to parse JSON response from URL: {err}")
        return []


def load_portfolio_from_file(filepath: str) -> List[Dict[str, Any]]:
    """Load portfolio data from a local JSON file."""
    if not os.path.exists(filepath):
        return []

    try:
        with open(filepath, "r", encoding="utf-8") as file_handle:
            data = json.load(file_handle)
            if isinstance(data, dict):
                return data.get("portfolio", [])
            if isinstance(data, list):
                return data
            return []
    except (json.JSONDecodeError, OSError) as err:
        print(f"❌ Failed to read local portfolio file ({filepath}): {err}")
        return []


def load_portfolio() -> List[Dict[str, Any]]:
    """Load portfolio data from Gist or local fallback file."""
    # 1. Try loading from GIST_ID if provided
    if GIST_ID:
        print(f"🌐 Fetching portfolio from GitHub Gist ID: {GIST_ID}...")
        portfolio = fetch_portfolio_from_gist_api(GIST_ID, token=GIST_TOKEN)
        if portfolio:
            return portfolio
        print("⚠️ Could not load from GIST_ID, checking fallback sources...")

    # 2. Try loading from PORTFOLIO_GIST_URL if provided
    if PORTFOLIO_GIST_URL:
        print("🌐 Fetching portfolio from PORTFOLIO_GIST_URL...")
        portfolio = fetch_portfolio_from_url(
            PORTFOLIO_GIST_URL, token=GIST_TOKEN
        )
        if portfolio:
            return portfolio
        print("⚠️ Could not load from URL, checking fallback sources...")

    # 3. Fallback to local file
    if os.path.exists(DEFAULT_PORTFOLIO_FILE):
        print(f"📁 Loading portfolio from local file: {DEFAULT_PORTFOLIO_FILE}")
        return load_portfolio_from_file(DEFAULT_PORTFOLIO_FILE)

    return []


def determine_status(diff_percent: float) -> str:
    """Return status emoji and label based on price difference percentage."""
    if diff_percent <= DIP_THRESHOLD_PERCENT:
        return "🚨 GOOD OPPORTUNITY TO AVERAGE DOWN 🚨"
    if diff_percent < 0:
        return "📉 Below Cost"
    return "📈 In Profit"


def fetch_stock_price(symbol: str) -> Optional[float]:
    """Fetch the latest price for a stock symbol using Yahoo Finance."""
    try:
        ticker = yf.Ticker(symbol)
        last_price = ticker.fast_info.get("lastPrice")
        if last_price is None:
            last_price = ticker.fast_info.get("regularMarketPrice")
        if last_price is not None:
            return float(last_price)
    except Exception as err:
        print(f"❌ Error fetching {symbol}: {err}")
    return None


def create_embed_field(item: Dict[str, Any]) -> Dict[str, Any]:
    """Build a Discord embed field for a single portfolio holding."""
    symbol = item.get("ticker", "UNKNOWN")
    avg_cost = item.get("avg_price", 0.0)

    current_price = fetch_stock_price(symbol)
    if current_price is None:
        return {
            "name": f"⚠️ Stock: {symbol}",
            "value": "Error fetching data. Check ticker symbol.",
            "inline": False,
        }

    diff_percent = ((current_price - avg_cost) / avg_cost) * 100
    status_text = determine_status(diff_percent)

    value_lines = [
        f"Current: ${current_price:.2f} | Avg: ${avg_cost:.2f}",
        f"Change: **{diff_percent:.2f}%**",
        f"Status: {status_text}",
    ]

    return {
        "name": f"🏢 Stock: {symbol}",
        "value": "\n".join(value_lines),
        "inline": False,
    }


def build_discord_payload(fields: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Construct the payload dictionary for Discord Webhook embed."""
    return {
        "embeds": [
            {
                "title": "📊 Daily Portfolio Status Report",
                "color": DEFAULT_EMBED_COLOR,
                "fields": fields,
                "footer": {"text": "Stock data from Yahoo Finance"},
            }
        ]
    }


def send_discord_notification(
    webhook_url: Optional[str],
    payload: Dict[str, Any],
) -> bool:
    """Send JSON payload to the Discord Webhook URL."""
    if not webhook_url:
        print("⚠️ Warning: DISCORD_WEBHOOK_URL is missing.")
        return False

    try:
        response = requests.post(
            webhook_url, json=payload, timeout=HTTP_TIMEOUT
        )
        response.raise_for_status()
        print("✅ Daily report sent to Discord.")
        return True
    except requests.RequestException as err:
        print(f"❌ Failed to send Discord notification: {err}")
        return False


def check_portfolio() -> None:
    """Check portfolio performance and dispatch Discord notification."""
    portfolio = load_portfolio()
    if not portfolio:
        print("🤷‍♂️ No stocks found in portfolio.")
        print(
            "💡 Tip: Set PORTFOLIO_GIST_URL / GIST_ID secret or create "
            "a local portfolio.json file."
        )
        return

    print(f"🔍 Starting portfolio check for {len(portfolio)} stocks...")

    fields: List[Dict[str, Any]] = []
    for item in portfolio:
        field = create_embed_field(item)
        fields.append(field)

    payload = build_discord_payload(fields)
    send_discord_notification(WEBHOOK_URL, payload)


if __name__ == "__main__":
    check_portfolio()
