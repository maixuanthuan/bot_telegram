# =============================================================================
# TELEGRAM DAILY BRIEF BOT — CONFIG
# =============================================================================

CONFIG = {
    # --- Telegram ---
    "BOT_TOKEN": "8976042318:AAHpV3IT0un-Hvxxqzn-Uq8OffNKYHjFsK8",
    "CHAT_ID": "1371153609",

    # --- OpenWeatherMap ---
    "WEATHER_API_KEY": "82925b0a1cff94d2d0393bec5b311e89",
    "WEATHER_CITY": "Hanoi",
    "WEATHER_COUNTRY": "VN",

    # --- GoldAPI.io ---
    "GOLD_API_KEY": "goldapi-033232fb98b61dad6beab2af6efea10a-io",

    # --- Stock HOSE (VNDirect API) ---
    "STOCK_SYMBOLS": ["FPT", "VCB", "TCB", "SSI", "PLX"],

    # --- Crypto (CoinGecko, free, không cần key) ---
    "CRYPTO_SYMBOLS": ["BTC", "ETH", "BNB", "SOL"],

    # --- AI News RSS ---
    "RSS_FEEDS": [
        {"name": "The Verge AI",    "url": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml"},
        {"name": "MIT Tech Review", "url": "https://www.technologyreview.com/feed/"},
        {"name": "VnExpress CN",    "url": "https://vnexpress.net/rss/khoa-hoc-cong-nghe.rss"},
    ],
    "NEWS_MAX_ITEMS": 4,

    # --- Scheduler ---
    "SCHEDULE_HOUR": 7,
    "SCHEDULE_MINUTE": 30,
    "TIMEZONE": "Asia/Ho_Chi_Minh",

    # --- Intraday Poll (giờ) ---
    "POLL_INTERVAL_HOURS": 1,

    # -------------------------------------------------------------------------
    # ALERT THRESHOLDS
    # -------------------------------------------------------------------------
    "THRESHOLDS": {
        "usd_pct":           0.3,
        "gold_pct":          100,
        "stock_pct":         1.0,
        "crypto_pct":        2.0,   # Crypto biến động mạnh hơn, để 2%
        "rain_pop_trigger":  70,
        "news_always_alert": True,
    },
}