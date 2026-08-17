"""
stock.py — Giá cổ phiếu HOSE dùng VNDirect public API.
"""
import requests
from config import CONFIG
from modules import state

THRESHOLD_PCT = CONFIG["THRESHOLDS"]["stock_pct"]
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
}


def _fetch_vndirect(symbol: str) -> dict | None:
    try:
        url = "https://api-finfo.vndirect.com.vn/v4/stock_prices"
        params = {"sort": "date", "q": f"code:{symbol}", "size": "1"}
        res = requests.get(url, params=params, headers=HEADERS, timeout=10)
        res.raise_for_status()
        items = res.json().get("data", [])
        if not items:
            return None
        row    = items[0]
        price  = float(row.get("close") or 0)
        change = float(row.get("change") or 0)
        pct    = float(row.get("pctChange") or 0)
        if price > 0:
            return {"symbol": symbol, "price": price, "change": change, "pct": pct}
    except Exception as e:
        print(f"[stock] VNDirect lỗi {symbol}: {e}")
    return None


def _fmt_line(symbol: str, price: float, change: float, pct: float) -> str:
    if change > 0:
        icon = "🟢"
        arrow = "▲"
        sign  = "+"
    elif change < 0:
        icon = "🔴"
        arrow = "▼"
        sign  = ""
    else:
        icon = "⚪"
        arrow = "—"
        sign  = ""
    return f"{icon} {symbol}: <b>{price:,.1f}</b> {arrow} {sign}{change:,.1f} ({sign}{pct:.2f}%)"


def fetch_stock() -> str:
    lines = ["📈 <b>STOCK</b>"]
    state_updates = {}

    for symbol in CONFIG["STOCK_SYMBOLS"]:
        data = _fetch_vndirect(symbol)
        if data:
            state_updates[f"stock_{symbol}"] = data["price"]
            lines.append(_fmt_line(symbol, data["price"], data["change"], data["pct"]))
        else:
            lines.append(f"⚪ {symbol}: <b>N/A</b>")

    if state_updates:
        state.set_many(state_updates)

    lines.append("Nguồn: VNDirect")
    return "\n".join(lines)


def check_alert() -> str | None:
    alerts = []

    for symbol in CONFIG["STOCK_SYMBOLS"]:
        data = _fetch_vndirect(symbol)
        if not data:
            continue

        price_now  = data["price"]
        price_prev = state.get(f"stock_{symbol}", 0)

        if price_prev == 0:
            state.set(f"stock_{symbol}", price_now)
            continue

        pct = abs(price_now - price_prev) / price_prev * 100

        if pct >= THRESHOLD_PCT:
            change = price_now - price_prev
            alerts.append(_fmt_line(symbol, price_now, change, pct if change > 0 else -pct))

        state.set(f"stock_{symbol}", price_now)

    if alerts:
        return "📈 <b>ALERT — STOCK</b>\n" + "\n".join(alerts) + "\nNguồn: VNDirect"
    return None