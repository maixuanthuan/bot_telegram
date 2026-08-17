"""
crypto.py — Giá crypto từ CoinGecko API (free, không cần key).
"""
import requests
from config import CONFIG
from modules import state

THRESHOLD_PCT = CONFIG["THRESHOLDS"]["crypto_pct"]
BASE_URL      = "https://api.coingecko.com/api/v3/simple/price"
HEADERS       = {"User-Agent": "Mozilla/5.0"}

COIN_IDS = {
    "BTC":  "bitcoin",
    "ETH":  "ethereum",
    "BNB":  "binancecoin",
    "SOL":  "solana",
    "XRP":  "ripple",
    "DOGE": "dogecoin",
}


def _fetch_prices(symbols: list) -> dict | None:
    try:
        ids = ",".join(COIN_IDS[s] for s in symbols if s in COIN_IDS)
        res = requests.get(BASE_URL, params={
            "ids": ids,
            "vs_currencies": "usd",
            "include_24hr_change": "true",
        }, headers=HEADERS, timeout=10)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        print(f"[crypto] CoinGecko lỗi: {e}")
    return None


def _fmt_line(symbol: str, price: float, chg: float) -> str:
    if chg > 0:
        icon = "🟢"; arrow = "▲"; sign = "+"
    elif chg < 0:
        icon = "🔴"; arrow = "▼"; sign = ""
    else:
        icon = "⚪"; arrow = "—"; sign = ""
    return f"{icon} {symbol}: <b>${price:,.2f}</b> {arrow} {sign}{chg:.2f}%"


def fetch_crypto() -> str:
    symbols = CONFIG["CRYPTO_SYMBOLS"]
    data    = _fetch_prices(symbols)
    if not data:
        return "🪙 <b>CRYPTO</b>\n⚠️ Không lấy được dữ liệu"

    lines         = ["🪙 <b>CRYPTO</b>"]
    state_updates = {}

    for symbol in symbols:
        coin_id = COIN_IDS.get(symbol)
        if not coin_id or coin_id not in data:
            lines.append(f"⚪ {symbol}: <b>N/A</b>")
            continue
        price  = float(data[coin_id].get("usd", 0))
        chg24h = float(data[coin_id].get("usd_24h_change", 0))
        state_updates[f"crypto_{symbol}"] = price
        lines.append(_fmt_line(symbol, price, chg24h))

    if state_updates:
        state.set_many(state_updates)

    lines.append("Nguồn: CoinGecko")
    return "\n".join(lines)


def check_alert() -> str | None:
    symbols = CONFIG["CRYPTO_SYMBOLS"]
    data    = _fetch_prices(symbols)
    if not data:
        return None

    alerts = []
    for symbol in symbols:
        coin_id = COIN_IDS.get(symbol)
        if not coin_id or coin_id not in data:
            continue

        price_now  = float(data[coin_id].get("usd", 0))
        price_prev = state.get(f"crypto_{symbol}", 0)

        if price_prev == 0:
            state.set(f"crypto_{symbol}", price_now)
            continue

        pct = abs(price_now - price_prev) / price_prev * 100

        if pct >= THRESHOLD_PCT:
            chg = price_now - price_prev
            alerts.append(_fmt_line(symbol, price_now, pct if chg > 0 else -pct))

        state.set(f"crypto_{symbol}", price_now)

    if alerts:
        return "🪙 <b>ALERT — CRYPTO</b>\n" + "\n".join(alerts) + "\nNguồn: CoinGecko"
    return None