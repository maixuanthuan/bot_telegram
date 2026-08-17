"""
poller.py — Gọi tất cả check_alert() mỗi 1 tiếng.
"""
from datetime import datetime
from modules.weather import check_alert as weather_alert
from modules.usd     import check_alert as usd_alert
from modules.gold    import check_alert as gold_alert
from modules.stock   import check_alert as stock_alert
from modules.crypto  import check_alert as crypto_alert
from modules.ai_news import check_alert as news_alert
from modules.sender  import send_alerts


def run_poll():
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[poller] Poll bắt đầu lúc {ts}")

    checkers = [
        ("weather", weather_alert),
        ("usd",     usd_alert),
        ("gold",    gold_alert),
        ("stock",   stock_alert),
        ("crypto",  crypto_alert),
        ("news",    news_alert),
    ]

    alerts = []
    for name, fn in checkers:
        try:
            result = fn()
            if result:
                print(f"[poller] ✅ Alert: {name}")
                alerts.append(result)
            else:
                print(f"[poller] — No change: {name}")
        except Exception as e:
            print(f"[poller] ❌ Lỗi {name}: {e}")

    if alerts:
        send_alerts(alerts)
    else:
        print("[poller] Không có thay đổi đáng kể.")