"""
sender.py — Gửi Telegram message.
"""
import requests
from datetime import datetime
from config import CONFIG
from modules.weather import fetch_weather
from modules.usd     import fetch_usd
from modules.gold    import fetch_gold
from modules.stock   import fetch_stock
from modules.crypto  import fetch_crypto
from modules.ai_news import fetch_ai_news

SEP = "━━━━━━━━━━━━━━━━━━"


def build_morning_brief() -> str:
    now = datetime.now().strftime("%d/%m/%Y %H:%M")
    sections = [
        f"☀️ <b>DAILY BRIEFING — {now}</b>",
        SEP,
        fetch_weather(),
        SEP,
        fetch_usd(),
        SEP,
        fetch_gold(),
        SEP,
        fetch_stock(),
        SEP,
        fetch_crypto(),
        SEP,
        fetch_ai_news(),
    ]
    return "\n".join(s for s in sections if s)


def build_alert(alerts: list[str]) -> str:
    now    = datetime.now().strftime("%H:%M")
    header = f"🔔 <b>UPDATE — {now}</b>\n{SEP}"
    body   = f"\n{SEP}\n".join(alerts)
    return f"{header}\n{body}"


def _send(text: str) -> bool:
    url     = f"https://api.telegram.org/bot{CONFIG['BOT_TOKEN']}/sendMessage"
    payload = {
        "chat_id":                  CONFIG["CHAT_ID"],
        "text":                     text,
        "parse_mode":               "HTML",
        "disable_web_page_preview": True,
    }
    try:
        res = requests.post(url, json=payload, timeout=15)
        res.raise_for_status()
        return True
    except Exception as e:
        print(f"[sender] Lỗi gửi Telegram: {e}")
        return False


def send_brief():
    print("[sender] Đang build morning brief...")
    msg = build_morning_brief()
    ok  = _send(msg)
    print(f"[sender] Morning brief {'✅ OK' if ok else '❌ FAIL'} lúc {datetime.now().strftime('%H:%M:%S')}")


def send_alerts(alerts: list[str]):
    if not alerts:
        return
    msg = build_alert(alerts)
    ok  = _send(msg)
    print(f"[sender] Alert ({len(alerts)} items) {'✅ OK' if ok else '❌ FAIL'} lúc {datetime.now().strftime('%H:%M:%S')}")