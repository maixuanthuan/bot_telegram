# 🤖 Telegram Daily Brief Bot

Bot tự động gửi brief buổi sáng + alert intraday khi có biến động đáng kể.

## Tính năng

- ☀️ **7:30 sáng** — Morning brief tổng hợp
- 🔔 **Mỗi 1 tiếng** — Poll intraday, gửi alert nếu vượt threshold
- 🟢🔴 Màu xanh/đỏ thể hiện tăng/giảm

## Nguồn dữ liệu

| Module | Nguồn | Ghi chú |
|--------|-------|---------|
| 🌦 Thời tiết | OpenWeatherMap API | Cần API key |
| 💵 USD/VND | Vietcombank XML | Public, không cần key |
| 🥇 Vàng | GoldAPI.io | Free 100 req/tháng, chỉ gọi 1 lần/ngày |
| 📈 Stock | VNDirect API | Public, không cần key |
| 🪙 Crypto | CoinGecko API | Free, không cần key |
| 🤖 AI News | RSS feeds | The Verge, MIT Tech Review, VnExpress |

## Cấu trúc

```
bot_telegram/
├── main.py              # Entry point
├── config.py            # Config + thresholds (secrets load từ .env)
├── requirements.txt
├── .env                 # Secrets (KHÔNG commit lên Git)
├── .env.example         # Template cho .env
└── modules/
    ├── weather.py
    ├── usd.py
    ├── gold.py
    ├── stock.py
    ├── crypto.py
    ├── ai_news.py
    ├── sender.py
    ├── poller.py
    └── state.py         # Đọc/ghi state.json (runtime cache)
```

## Cài đặt

```bash
# 1. Clone repo
git clone https://github.com/maixuanthuan/bot_telegram.git
cd bot_telegram

# 2. Cài dependencies
pip install -r requirements.txt

# 3. Tạo file .env
cp .env.example .env
# Điền API keys vào .env

# 4. Test
python main.py test    # Kiểm tra từng module
python main.py now     # Gửi brief lên Telegram ngay
python main.py poll    # Test alert intraday
```

## Deploy 24/7 với systemd

```bash
sudo nano /etc/systemd/system/tgbot.service
```

```ini
[Unit]
Description=Telegram Daily Brief Bot
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/home/YOUR_USERNAME/bot_telegram
ExecStart=/usr/bin/python3 /home/YOUR_USERNAME/bot_telegram/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable tgbot
sudo systemctl start tgbot
sudo journalctl -u tgbot -f  # Xem log realtime
```

## Config thresholds

```python
"THRESHOLDS": {
    "usd_pct":           0.3,    # USD/VND thay đổi >= 0.3%
    "gold_pct":          100.0,  # Gold không alert intraday
    "stock_pct":         1.0,    # Stock thay đổi >= 1.0%
    "crypto_pct":        2.0,    # Crypto thay đổi >= 2.0%
    "rain_pop_trigger":  70,     # Mưa >= 70%
    "news_always_alert": True,   # Luôn alert khi có tin mới
}
```

## Lịch chạy

- **7:30 sáng**: Morning brief đầy đủ
- **Mỗi 1 tiếng**: Poll intraday, gửi alert nếu có biến động