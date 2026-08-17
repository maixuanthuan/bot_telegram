"""
usd.py — Tỷ giá USD/VND từ Vietcombank (public XML, không cần API key).
Endpoint: https://portal.vietcombank.com.vn/Usercontrols/TVPortal.TyGia/pXML.aspx?b=10
Fallback: ExchangeRate-API (open.er-api.com)
"""
import requests
from bs4 import BeautifulSoup
from config import CONFIG
from modules import state

THRESHOLD_PCT = CONFIG["THRESHOLDS"]["usd_pct"]


def _parse_vnd(raw: str) -> float:
    """
    Vietcombank XML trả về dạng '25.990,00' (dấu chấm = nghìn, phẩy = thập phân)
    Hoặc dạng '25990' thuần số.
    -> Luôn trả về số thực, ví dụ 25990.0
    """
    try:
        s = raw.strip()
        # Nếu có cả dấu chấm lẫn phẩy: '25.990,00' -> bỏ chấm, đổi phẩy thành chấm
        if "." in s and "," in s:
            s = s.replace(".", "").replace(",", ".")
        # Chỉ có dấu chấm: có thể là '25.990' (nghìn) hoặc '25.9' (thập phân)
        elif "." in s:
            parts = s.split(".")
            # Nếu phần thập phân <= 2 chữ số và tổng > 5 chữ -> nghìn phân cách
            if len(parts[-1]) >= 3:
                s = s.replace(".", "")   # '25.990' -> '25990'
            # else giữ nguyên (số thập phân thật)
        # Chỉ có dấu phẩy: '25,990' -> bỏ phẩy
        elif "," in s:
            parts = s.split(",")
            if len(parts[-1]) >= 3:
                s = s.replace(",", "")
            else:
                s = s.replace(",", ".")
        return float(s)
    except Exception:
        return 0.0


def _fetch_vcb() -> dict | None:
    """Lấy tỷ giá từ Vietcombank XML."""
    try:
        url = "https://portal.vietcombank.com.vn/Usercontrols/TVPortal.TyGia/pXML.aspx?b=10"
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.content, "xml")
        for ex in soup.find_all("Exrate"):
            if ex.get("CurrencyCode") == "USD":
                buy  = _parse_vnd(ex.get("Buy", "0"))
                sell = _parse_vnd(ex.get("Sell", "0"))
                if sell > 0:
                    return {"buy": buy, "sell": sell, "source": "Vietcombank"}
    except Exception as e:
        print(f"[usd] VCB lỗi: {e}")
    return None


def _fetch_fallback() -> dict | None:
    """Fallback: ExchangeRate-API (free, 1 lần/ngày nhưng vẫn hữu ích)."""
    try:
        res = requests.get("https://open.er-api.com/v6/latest/USD", timeout=10)
        res.raise_for_status()
        data = res.json()
        rate = data["rates"].get("VND", 0)
        if rate > 0:
            return {"buy": rate, "sell": rate, "source": "ExchangeRate-API"}
    except Exception as e:
        print(f"[usd] Fallback lỗi: {e}")
    return None


def fetch_usd_raw() -> dict | None:
    """Trả về dict {buy, sell, source} hoặc None nếu lỗi cả hai nguồn."""
    return _fetch_vcb() or _fetch_fallback()


def fetch_usd() -> str:
    """Dùng cho morning brief — luôn trả về block text."""
    data = fetch_usd_raw()
    if not data:
        return "💵 <b>TỶ GIÁ</b>\n⚠️ Không lấy được dữ liệu"

    sell = data["sell"]
    buy  = data["buy"]
    src  = data["source"]

    # Lưu state
    state.set("usd_sell", sell)

    return (
        f"💵 <b>TỶ GIÁ USD/VND</b>\n"
        f"Mua: <b>{buy:,.0f}</b> — Bán: <b>{sell:,.0f}</b>\n"
        f"Nguồn: {src}"
    )


def check_alert() -> str | None:
    """
    Gọi mỗi 1 tiếng. So sánh giá bán hiện tại với state trước.
    Trả về alert text nếu vượt threshold, None nếu không.
    """
    data = fetch_usd_raw()
    if not data:
        return None

    sell_now  = data["sell"]
    sell_prev = state.get("usd_sell", 0)

    if sell_prev == 0:
        state.set("usd_sell", sell_now)
        return None

    pct = abs(sell_now - sell_prev) / sell_prev * 100

    if pct >= THRESHOLD_PCT:
        arrow  = "↗️" if sell_now > sell_prev else "↘️"
        sign   = "+" if sell_now > sell_prev else "-"
        diff   = abs(sell_now - sell_prev)
        state.set("usd_sell", sell_now)
        return (
            f"💵 <b>ALERT — TỶ GIÁ USD/VND</b>\n"
            f"{arrow} Giá bán: <b>{sell_now:,.0f}</b>\n"
            f"Thay đổi: {sign}{diff:,.0f} ({sign}{pct:.2f}%)\n"
            f"Nguồn: {data['source']}"
        )

    # Cập nhật state dù không alert
    state.set("usd_sell", sell_now)
    return None