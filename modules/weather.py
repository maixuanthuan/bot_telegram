"""
weather.py — Thời tiết OpenWeatherMap.
Alert khi rain pop tăng lên >= threshold so với lần poll trước.
"""
import requests
from config import CONFIG
from modules import state

RAIN_TRIGGER = CONFIG["THRESHOLDS"]["rain_pop_trigger"]

WEATHER_EMOJI = {
    "Clear": "☀️", "Clouds": "☁️", "Rain": "🌧️",
    "Drizzle": "🌦️", "Thunderstorm": "⛈️", "Snow": "❄️",
    "Mist": "🌫️", "Fog": "🌫️", "Haze": "🌫️",
}


def _call_api() -> list | None:
    try:
        url = "https://api.openweathermap.org/data/2.5/forecast"
        params = {
            "q": f"{CONFIG['WEATHER_CITY']},{CONFIG['WEATHER_COUNTRY']}",
            "appid": CONFIG["WEATHER_API_KEY"],
            "units": "metric",
            "lang": "vi",
            "cnt": 8,
        }
        res = requests.get(url, params=params, timeout=10)
        res.raise_for_status()
        return res.json()["list"]
    except Exception as e:
        print(f"[weather] API lỗi: {e}")
        return None


def fetch_weather() -> str:
    items = _call_api()
    if not items:
        return "🌦 <b>THỜI TIẾT</b>\n⚠️ Không lấy được dữ liệu"

    current = items[0]
    main    = current["weather"][0]["main"]
    desc    = current["weather"][0]["description"].capitalize()
    emoji   = WEATHER_EMOJI.get(main, "🌤️")

    temps       = [i["main"]["temp"] for i in items]
    temp_min    = min(temps)
    temp_max    = max(temps)

    pops        = [i.get("pop", 0) * 100 for i in items]
    rain_chance = max(pops)

    # Lưu state
    state.set("weather_rain_pop", rain_chance)

    warning = ""
    if rain_chance >= RAIN_TRIGGER:
        afternoon = items[3:]
        if afternoon and max(x.get("pop", 0) for x in afternoon) >= 0.6:
            warning = "\n⚠️ Có khả năng mưa lớn buổi chiều"
        else:
            warning = "\n⚠️ Có khả năng mưa lớn trong ngày"

    return (
        f"🌦 <b>THỜI TIẾT — Hà Nội</b>\n"
        f"{temp_min:.0f}°C → {temp_max:.0f}°C\n"
        f"{emoji} {desc}\n"
        f"Khả năng mưa: {rain_chance:.0f}%"
        f"{warning}"
    )


def check_alert() -> str | None:
    items = _call_api()
    if not items:
        return None

    pops        = [i.get("pop", 0) * 100 for i in items]
    rain_now    = max(pops)
    rain_prev   = state.get("weather_rain_pop", 0)

    state.set("weather_rain_pop", rain_now)

    # Alert khi vượt ngưỡng mưa (và lần trước chưa trigger)
    if rain_now >= RAIN_TRIGGER and rain_prev < RAIN_TRIGGER:
        desc  = items[0]["weather"][0]["description"].capitalize()
        temps = [i["main"]["temp"] for i in items]
        return (
            f"🌧️ <b>ALERT — THỜI TIẾT</b>\n"
            f"Khả năng mưa tăng lên <b>{rain_now:.0f}%</b>!\n"
            f"Nhiệt độ: {min(temps):.0f}°C → {max(temps):.0f}°C\n"
            f"{desc}\n"
            f"⚠️ Nhớ mang ô nhé!"
        )

    return None