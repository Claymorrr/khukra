"""Curated low-latency RSS feeds for logistics disruption headlines."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class NewsFeed:
    feed_id: str
    label: str
    url: str
    category: str


NEWS_FEEDS: tuple[NewsFeed, ...] = (
    NewsFeed("bbc_business", "BBC Business", "http://feeds.bbci.co.uk/news/business/rss.xml", "macro"),
    NewsFeed("freightwaves", "FreightWaves", "https://www.freightwaves.com/feed", "shipping"),
    NewsFeed(
        "supplychain_dive",
        "Supply Chain Dive",
        "https://www.supplychaindive.com/feeds/news/",
        "logistics",
    ),
    NewsFeed("reuters_business", "Reuters Business", "https://feeds.reuters.com/reuters/businessNews", "macro"),
    NewsFeed("aj_world", "Al Jazeera", "https://www.aljazeera.com/xml/rss/all.xml", "geopolitics"),
)

FEEDS_BY_ID: dict[str, NewsFeed] = {f.feed_id: f for f in NEWS_FEEDS}
