# Telegram Daily Brief Bot

Bot tự động gửi brief buổi sáng + alert intraday mỗi khi có biến động đáng kể.

## Cấu trúc

```
telegram_bot/
├── main.py              # Entry point
├── config.py            # Toàn bộ config + threshold
├── requirements.txt
├── state.json           # Tự tạo khi chạy (lưu giá trị poll trước)
└── modules/
    ├── weather.py       # Thời tiết OpenWeatherMap
    ├── usd.py           # Tỷ giá (Vietcombank → fallback ExchangeRate)
    ├── gold.py          # Vàng SJC (sjc.com.vn XML → fallback btmc.vn)
    ├── stock.py         # Cổ phiếu (SSI → Vietstock → CafeF)
    ├── hardware.py      # Giá PC GearVN
    ├── ai_news.py       # RSS AI News
    ├── sender.py        # Gửi Telegram
    ├── poller.py        # Gom tất cả alert mỗi 1 tiếng
    └── state.py         # Đọc/ghi state.json
```

## Cài đặt trên Ubuntu

```bash
# 1. Clone / copy code vào server
cd ~
mkdir telegram_bot && cd telegram_bot
# (copy files vào đây)

# 2. Cài dependencies
pip3 install -r requirements.txt

# 3. Test các module (không gửi Telegram)
python3 main.py test

# 4. Gửi brief ngay để test Telegram
python3 main.py now

# 5. Test poll alert ngay
python3 main.py poll
```

## Deploy chạy 24/7 với systemd

```bash
# Tạo service file
sudo nano /etc/systemd/system/tgbot.service
```

Nội dung file:
```ini
[Unit]
Description=Telegram Daily Brief Bot
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/home/YOUR_USERNAME/telegram_bot
ExecStart=/usr/bin/python3 /home/YOUR_USERNAME/telegram_bot/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable và start
sudo systemctl daemon-reload
sudo systemctl enable tgbot
sudo systemctl start tgbot

# Xem log
sudo journalctl -u tgbot -f
```

## Config thresholds (config.py)

```python
"THRESHOLDS": {
    "usd_pct":         0.3,   # Alert khi USD/VND thay đổi >= 0.3%
    "gold_pct":        0.5,   # Alert khi vàng SJC thay đổi >= 0.5%
    "stock_pct":       1.0,   # Alert khi cổ phiếu thay đổi >= 1.0%
    "hardware_pct":    2.0,   # Alert khi giá hardware thay đổi >= 2.0%
    "rain_pop_trigger": 70,   # Alert khi khả năng mưa tăng lên >= 70%
    "news_always_alert": True, # Luôn alert khi có bài AI News mới
}
```

## Nguồn dữ liệu

| Module   | Nguồn chính          | Fallback        |
|----------|----------------------|-----------------|
| USD/VND  | Vietcombank XML      | ExchangeRate-API|
| Vàng SJC | sjc.com.vn/xml       | btmc.vn scrape  |
| Stock    | SSI iBoard API       | Vietstock → CafeF |
| Weather  | OpenWeatherMap       | —               |
| Hardware | GearVN scrape        | —               |
| AI News  | RSS (Verge/MIT/VNE)  | —               |

## Lịch chạy

- **7:30 sáng**: Morning brief đầy đủ
- **Mỗi 1 tiếng**: Poll tất cả nguồn, gửi alert nếu vượt threshold