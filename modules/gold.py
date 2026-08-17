"""
gold.py — Giá vàng dùng GoldAPI.io (XAU/USD) convert sang VNĐ/lượng.

Công thức:
  - 1 troy oz = 31.1035 gram
  - 1 lượng VN = 37.5 gram
  - 1 lượng = 37.5 / 31.1035 troy oz = 1.2057 troy oz
  - Giá VNĐ/lượng = price_usd_per_oz * 1.2057 * usd_vnd_rate

USD/VND lấy từ Vietcombank XML (đã có sẵn trong usd.py).
Fallback USD/VND: tỷ giá cứng nếu không lấy được.
"""
import requests
from config import CONFIG
from modules import state

THRESHOLD_PCT  = CONFIG["THRESHOLDS"]["gold_pct"]
LUONG_PER_OZ   = 37.5 / 31.1035   # 1 lượng = 1.2057 troy oz
GOLD_API_KEY   = CONFIG["GOLD_API_KEY"]
HEADERS_GOLD   = {
    "x-access-token": GOLD_API_KEY,
    "Content-Type":   "application/json",
}
HEADERS_VCB = {"User-Agent": "Mozilla/5.0"}


def _get_usd_vnd() -> float:
    """Lấy tỷ giá USD/VND từ Vietcombank XML. Fallback = 25900."""
    try:
        from bs4 import BeautifulSoup
        url = "https://portal.vietcombank.com.vn/Usercontrols/TVPortal.TyGia/pXML.aspx?b=10"
        res = requests.get(url, headers=HEADERS_VCB, timeout=8)
        res.raise_for_status()
        soup = BeautifulSoup(res.content, "xml")
        for ex in soup.find_all("Exrate"):
            if ex.get("CurrencyCode") == "USD":
                raw  = ex.get("Sell", "0")
                s    = raw.strip()
                if "." in s and "," in s:
                    s = s.replace(".", "").replace(",", ".")
                elif "." in s and len(s.split(".")[-1]) >= 3:
                    s = s.replace(".", "")
                elif "," in s and len(s.split(",")[-1]) >= 3:
                    s = s.replace(",", "")
                val = float(s)
                if val > 1000:
                    return val
    except Exception as e:
        print(f"[gold] VCB tỷ giá lỗi: {e}")
    return 25900.0  # fallback


def _fetch_goldapi() -> dict | None:
    """GoldAPI.io — trả về giá XAU theo USD/oz."""
    try:
        url = "https://www.goldapi.io/api/XAU/USD"
        res = requests.get(url, headers=HEADERS_GOLD, timeout=10)
        res.raise_for_status()
        data     = res.json()
        price_oz = float(data.get("price") or data.get("price_gram_24k") or 0)
        # price là USD/oz
        if price_oz > 0:
            return {"price_oz": price_oz, "source": "GoldAPI.io"}
    except Exception as e:
        print(f"[gold] GoldAPI lỗi: {e}")
    return None


def _calc_vnd_luong(price_oz: float, usd_vnd: float) -> float:
    """Tính giá VNĐ/lượng từ USD/oz."""
    return price_oz * LUONG_PER_OZ * usd_vnd


def fetch_gold_raw() -> dict | None:
    data = _fetch_goldapi()
    if not data:
        return None
    usd_vnd   = _get_usd_vnd()
    price_vnd = _calc_vnd_luong(data["price_oz"], usd_vnd)
    return {
        "price_oz":  data["price_oz"],
        "price_vnd": price_vnd,
        "usd_vnd":   usd_vnd,
        "source":    data["source"],
    }


def fetch_gold() -> str:
    data = fetch_gold_raw()
    if not data:
        return "🥇 <b>VÀNG</b>\n⚠️ Không lấy được dữ liệu"

    price_vnd = data["price_vnd"]
    price_oz  = data["price_oz"]
    state.set("gold_vnd", price_vnd)

    return (
        f"🥇 <b>VÀNG QUỐC TẾ</b>\n"
        f"XAU/USD: <b>${price_oz:,.2f}</b>/oz\n"
        f"≈ <b>{price_vnd/1_000_000:.2f}M</b> VNĐ/lượng\n"
        f"Nguồn: {data['source']}"
    )


def check_alert() -> str | None:
    data = fetch_gold_raw()
    if not data:
        return None

    price_now  = data["price_vnd"]
    price_prev = state.get("gold_vnd", 0)

    if price_prev == 0:
        state.set("gold_vnd", price_now)
        return None

    pct = abs(price_now - price_prev) / price_prev * 100

    if pct >= THRESHOLD_PCT:
        arrow = "↗️" if price_now > price_prev else "↘️"
        sign  = "+" if price_now > price_prev else "-"
        diff  = abs(price_now - price_prev)
        state.set("gold_vnd", price_now)
        return (
            f"🥇 <b>ALERT — VÀNG</b>\n"
            f"{arrow} XAU/USD: <b>${data['price_oz']:,.2f}</b>/oz\n"
            f"≈ <b>{price_now/1_000_000:.2f}M</b> VNĐ/lượng\n"
            f"Thay đổi: {sign}{diff/1_000_000:.2f}M ({sign}{pct:.2f}%)\n"
            f"Nguồn: {data['source']}"
        )

    state.set("gold_vnd", price_now)
    return None