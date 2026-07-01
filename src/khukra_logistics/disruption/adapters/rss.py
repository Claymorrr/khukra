"""RSS/Atom fetch and parse — stdlib only for low dependency latency."""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Any
from urllib.request import Request, urlopen

_USER_AGENT = "KhukraLogistics/0.1 (disruption research; +https://github.com/local)"
_TIMEOUT = 12


@dataclass
class RssEntry:
    feed_id: str
    title: str
    link: str
    published_at: datetime
    summary: str


def _strip_ns(tag: str) -> str:
    return tag.split("}")[-1] if "}" in tag else tag


def _parse_date(raw: str | None) -> datetime | None:
    if not raw or not raw.strip():
        return None
    raw = raw.strip()
    try:
        return parsedate_to_datetime(raw).astimezone(timezone.utc)
    except (TypeError, ValueError, IndexError):
        pass
    for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(raw.replace("Z", "+0000"), fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        except ValueError:
            continue
    return None


def _text(elem: ET.Element | None) -> str:
    if elem is None:
        return ""
    return re.sub(r"\s+", " ", "".join(elem.itertext())).strip()


def fetch_feed(feed_id: str, url: str) -> list[RssEntry]:
    """Fetch and parse RSS 2.0 or Atom entries."""
    req = Request(url, headers={"User-Agent": _USER_AGENT})
    with urlopen(req, timeout=_TIMEOUT) as resp:
        payload = resp.read()

    root = ET.fromstring(payload)
    root_tag = _strip_ns(root.tag).lower()
    entries: list[RssEntry] = []

    if root_tag == "rss":
        channel = root.find("channel")
        items = channel.findall("item") if channel is not None else []
        for item in items:
            title = _text(item.find("title"))
            link = _text(item.find("link"))
            pub = _parse_date(_text(item.find("pubDate")))
            summary = _text(item.find("description"))
            if title and pub:
                entries.append(RssEntry(feed_id, title, link or title, pub, summary))
    elif root_tag == "feed":  # Atom
        for entry in root.findall("{*}entry") or root.findall("entry"):
            title = _text(entry.find("{*}title") or entry.find("title"))
            link_el = entry.find("{*}link") or entry.find("link")
            link = link_el.get("href", "") if link_el is not None else ""
            updated = entry.find("{*}updated") or entry.find("updated")
            published = entry.find("{*}published") or entry.find("published")
            pub = _parse_date(_text(updated)) or _parse_date(_text(published))
            summary = _text(entry.find("{*}summary") or entry.find("summary"))
            if title and pub:
                entries.append(RssEntry(feed_id, title, link or title, pub, summary))
    return entries


def entries_to_records(entries: list[RssEntry]) -> list[dict[str, Any]]:
    return [
        {
            "feed_id": e.feed_id,
            "title": e.title,
            "link": e.link,
            "published_at": e.published_at,
            "summary": e.summary,
        }
        for e in entries
    ]
