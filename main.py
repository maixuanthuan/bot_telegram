"""
main.py — Entry point.

Cách dùng:
  python main.py          → Chạy scheduler (7:30 brief + poll mỗi 1h)
  python main.py now      → Gửi morning brief ngay lập tức
  python main.py poll     → Chạy poll intraday ngay (test alert)
  python main.py test     → Test tất cả modules, in ra console
"""
import sys
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron       import CronTrigger
from apscheduler.triggers.interval   import IntervalTrigger
from config import CONFIG
from modules.sender import send_brief
from modules.poller import run_poll


def run_test():
    """In output của từng module ra console để debug."""
    print("\n" + "="*50)
    print("TEST MODE — Kiểm tra từng module")
    print("="*50)

    from modules.weather  import fetch_weather
    from modules.usd      import fetch_usd
    from modules.gold     import fetch_gold
    from modules.stock    import fetch_stock
    from modules.hardware import fetch_hardware
    from modules.ai_news  import fetch_ai_news

    modules = [
        ("WEATHER",  fetch_weather),
        ("USD",      fetch_usd),
        ("GOLD",     fetch_gold),
        ("STOCK",    fetch_stock),
        ("HARDWARE", fetch_hardware),
        ("AI NEWS",  fetch_ai_news),
    ]

    for name, fn in modules:
        print(f"\n--- {name} ---")
        try:
            result = fn()
            # Strip HTML tags để dễ đọc trong terminal
            import re
            clean = re.sub(r"<[^>]+>", "", result)
            print(clean)
        except Exception as e:
            print(f"❌ Lỗi: {e}")

    print("\n" + "="*50)
    print("TEST XONG")
    print("="*50 + "\n")


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""

    if cmd == "now":
        print("[main] Gửi morning brief ngay...")
        send_brief()
        return

    if cmd == "poll":
        print("[main] Chạy poll intraday ngay...")
        run_poll()
        return

    if cmd == "test":
        run_test()
        return

    # --- Chế độ scheduler bình thường ---
    scheduler = BlockingScheduler(timezone=CONFIG["TIMEZONE"])

    # Morning brief: 7:30 mỗi ngày
    scheduler.add_job(
        send_brief,
        trigger=CronTrigger(
            hour=CONFIG["SCHEDULE_HOUR"],
            minute=CONFIG["SCHEDULE_MINUTE"],
            timezone=CONFIG["TIMEZONE"],
        ),
        id="morning_brief",
        replace_existing=True,
    )

    # Intraday poll: mỗi N tiếng
    scheduler.add_job(
        run_poll,
        trigger=IntervalTrigger(hours=CONFIG["POLL_INTERVAL_HOURS"]),
        id="intraday_poll",
        replace_existing=True,
    )

    h = CONFIG["SCHEDULE_HOUR"]
    m = CONFIG["SCHEDULE_MINUTE"]
    p = CONFIG["POLL_INTERVAL_HOURS"]
    print(f"[main] ✅ Scheduler khởi động.")
    print(f"[main] 📅 Morning brief: {h:02d}:{m:02d} mỗi ngày")
    print(f"[main] 🔄 Intraday poll: mỗi {p} tiếng")
    print(f"[main] Ctrl+C để dừng.\n")

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("\n[main] Bot đã dừng.")


if __name__ == "__main__":
    main()