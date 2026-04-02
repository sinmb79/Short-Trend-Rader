from __future__ import annotations

import json

from trend_radar.collectors.google_trends import GoogleTrendsCollector
from trend_radar.collectors.naver import NaverDataLabCollector
from trend_radar.collectors.reddit import RedditCollector
from trend_radar.collectors.rss_generic import RSSGenericCollector
from trend_radar.collectors.youtube import YouTubeCollector
from trend_radar.config.schema import FeedConfig


def test_youtube_parser_extracts_items() -> None:
    payload = {
        "contents": {
            "twoColumnBrowseResultsRenderer": {
                "tabs": [
                    {
                        "tabRenderer": {
                            "content": {
                                "sectionListRenderer": {
                                    "contents": [
                                        {
                                            "itemSectionRenderer": {
                                                "contents": [
                                                    {
                                                        "videoRenderer": {
                                                            "videoId": "abc123",
                                                            "title": {"runs": [{"text": "AI build log"}]},
                                                            "descriptionSnippet": {"runs": [{"text": "#AI prototype"}]},
                                                            "ownerText": {"runs": [{"text": "22B Labs"}]},
                                                            "viewCountText": {"simpleText": "1.2M views"},
                                                            "thumbnail": {"thumbnails": [{"url": "https://example.com/thumb.jpg"}]},
                                                        }
                                                    }
                                                ]
                                            }
                                        }
                                    ]
                                }
                            }
                        }
                    }
                ]
            }
        }
    }
    html = f"<script>var ytInitialData = {json.dumps(payload)};</script>"
    items = YouTubeCollector._parse_listing(html=html, region="US", category="trending")
    assert len(items) == 1
    assert items[0].item_id == "abc123"
    assert items[0].metrics["views"] == 1_200_000


def test_reddit_parser_extracts_items() -> None:
    payload = {
        "data": {
            "children": [
                {
                    "data": {
                        "id": "post1",
                        "title": "Launch day notes",
                        "permalink": "/r/technology/comments/post1/launch_day_notes/",
                        "selftext": "What shipped today",
                        "author": "sinmb79",
                        "ups": 42,
                        "num_comments": 7,
                        "score": 40,
                    }
                }
            ]
        }
    }
    items = RedditCollector._parse_listing(subreddit="technology", payload=payload)
    assert len(items) == 1
    assert items[0].url.endswith("/launch_day_notes/")
    assert items[0].metrics["ups"] == 42


def test_rss_parser_extracts_items() -> None:
    entry = {
        "title": "A better trend feed",
        "link": "https://example.com/post",
        "summary": "Notes on shipping useful tooling",
        "author": "22B Labs",
        "id": "rss-1",
    }
    items = RSSGenericCollector._parse_feed(feed=FeedConfig(name="Example Feed", url="https://example.com/rss"), payload=[entry])
    assert len(items) == 1
    assert items[0].platform == "rss_generic"
    assert "trend" in " ".join(items[0].keywords).casefold()


def test_google_trends_build_items() -> None:
    items = GoogleTrendsCollector._build_items(region="KR", terms=["AI", "robot"])
    assert len(items) == 2
    assert items[0].platform == "google_trends"
    assert items[0].trend_score > items[1].trend_score


def test_naver_skips_without_env(monkeypatch) -> None:
    monkeypatch.delenv("NAVER_CLIENT_ID", raising=False)
    monkeypatch.delenv("NAVER_CLIENT_SECRET", raising=False)
    collector = NaverDataLabCollector()
    assert collector.is_available() is True
