DEFAULT_CONFIG: dict = {
    "collectors": {
        "youtube": {
            "enabled": True,
            "regions": ["KR", "US"],
            "categories": ["trending", "shorts"],
            "max_items": 20,
        },
        "reddit": {
            "enabled": True,
            "subreddits": ["popular", "technology", "videos"],
            "sort": "hot",
            "max_items": 15,
        },
        "google_trends": {
            "enabled": True,
            "regions": ["KR", "US"],
            "max_items": 10,
        },
        "rss_generic": {
            "enabled": True,
            "feeds": [
                {"name": "Hacker News", "url": "https://hnrss.org/frontpage"},
                {"name": "TechCrunch", "url": "https://techcrunch.com/feed/"},
            ],
            "max_items": 20,
        },
        "naver_datalab": {
            "enabled": True,
            "client_id_env": "NAVER_CLIENT_ID",
            "client_secret_env": "NAVER_CLIENT_SECRET",
            "max_items": 10,
            "keyword_groups": [],
        },
    },
    "interests": {
        "keywords": ["AI", "startup", "creator"],
        "categories": ["tech", "business", "lifestyle"],
        "exclude_keywords": [],
    },
    "schedule": {
        "mode": "once",
        "intervals": {"tier1": "1h", "tier2": "6h", "tier3": "12h"},
    },
    "output": {
        "base_dir": "~/.22b/trends",
        "formats": ["md", "json"],
        "digest": True,
        "alerts": {
            "enabled": True,
            "spike_threshold": 3.0,
            "keywords": ["AI", "GPT"],
        },
    },
    "limits": {
        "max_storage_gb": 5,
        "cleanup_after_days": 30,
    },
}
