"""
ai_news.py — RSS AI News.
Alert khi có bài mới chưa thấy trước đó (so sánh bằng link/title hash).
"""
import hashlib
import feedparser
from config import CONFIG
from modules import state

ALWAYS_ALERT = CONFIG["THRESHOLDS"]["news_always_alert"]
MAX_ITEMS    = CONFIG["NEWS_MAX_ITEMS"]


def _hash(title: str, link: str) -> str:
    return hashlib.md5(f"{title}{link}".encode()).hexdigest()[:12]


def _fetch_entries() -> list[dict]:
    """Lấy tất cả entries từ các RSS feed, trả về list {title, link, source, hash}."""
    entries = []
    for feed_cfg in CONFIG["RSS_FEEDS"]:
        try:
            feed = feedparser.parse(feed_cfg["url"])
            for entry in feed.entries[:3]:
                title = entry.get("title", "").strip()
                link  = entry.get("link", "")
                if not title:
                    continue
                if len(title) > 90:
                    title = title[:87] + "..."
                entries.append({
                    "title":  title,
                    "link":   link,
                    "source": feed_cfg["name"],
                    "hash":   _hash(title, link),
                })
        except Exception as e:
            print(f"[ai_news] Lỗi feed {feed_cfg['name']}: {e}")
    return entries


def fetch_ai_news() -> str:
    entries = _fetch_entries()
    if not entries:
        return "🤖 <b>AI NEWS</b>\n⚠️ Không lấy được tin tức hôm nay"

    shown  = entries[:MAX_ITEMS]
    lines  = ["🤖 <b>AI NEWS</b>"]

    seen_hashes = set(state.get("news_seen_hashes", []))
    new_hashes  = {e["hash"] for e in shown}

    for i, e in enumerate(shown, 1):
        lines.append(f'{i}. <a href="{e["link"]}">{e["title"]}</a>')

    # Cập nhật state: chỉ giữ 50 hash gần nhất
    all_hashes = list(new_hashes | seen_hashes)[-50:]
    state.set("news_seen_hashes", all_hashes)

    return "\n".join(lines)


def check_alert() -> str | None:
    if not ALWAYS_ALERT:
        return None

    entries     = _fetch_entries()
    seen_hashes = set(state.get("news_seen_hashes", []))

    new_entries = [e for e in entries if e["hash"] not in seen_hashes]
    if not new_entries:
        return None

    shown = new_entries[:MAX_ITEMS]
    lines = ["🤖 <b>AI NEWS MỚI</b>"]
    for i, e in enumerate(shown, 1):
        lines.append(f'{i}. <a href="{e["link"]}">{e["title"]}</a> — <i>{e["source"]}</i>')

    # Cập nhật seen
    new_hashes  = {e["hash"] for e in shown}
    all_hashes  = list(new_hashes | seen_hashes)[-50:]
    state.set("news_seen_hashes", all_hashes)

    return "\n".join(lines)