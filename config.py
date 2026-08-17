import os
from dotenv import load_dotenv

load_dotenv()

CONFIG = {
    "BOT_TOKEN": os.getenv("BOT_TOKEN"),
    "CHAT_ID":   os.getenv("CHAT_ID"),
    "WEATHER_API_KEY": os.getenv("WEATHER_API_KEY"),
    "WEATHER_CITY":    "Hanoi",
    "WEATHER_COUNTRY": "VN",
    "GOLD_API_KEY": os.getenv("GOLD_API_KEY"),
    "STOCK_SYMBOLS":  ["FPT", "VCB", "TCB", "SSI", "PLX"],
    "CRYPTO_SYMBOLS": ["BTC", "ETH", "BNB", "SOL"],
    "RSS_FEEDS": [
        {"name": "The Verge AI",    "url": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml"},
        {"name": "MIT Tech Review", "url": "https://www.technologyreview.com/feed/"},
        {"name": "VnExpress CN",    "url": "https://vnexpress.net/rss/khoa-hoc-cong-nghe.rss"},
    ],
    "NEWS_MAX_ITEMS": 4,
    "SCHEDULE_HOUR":   7,
    "SCHEDULE_MINUTE": 30,
    "TIMEZONE":        "Asia/Ho_Chi_Minh",
    "POLL_INTERVAL_HOURS": 1,
    "THRESHOLDS": {
        "usd_pct":           0.3,
        "gold_pct":          100.0,
        "stock_pct":         1.0,
        "crypto_pct":        2.0,
        "rain_pop_trigger":  70,
        "news_always_alert": True,
    },
}
