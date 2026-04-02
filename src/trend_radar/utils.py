from __future__ import annotations

import math
import re
from collections import Counter
from pathlib import Path


WORD_PATTERN = re.compile(r"[0-9A-Za-z가-힣][0-9A-Za-z가-힣_+\-]{1,}")
HASHTAG_PATTERN = re.compile(r"#([0-9A-Za-z가-힣_]+)")
URL_PATTERN = re.compile(r"https?://\S+|www\.\S+", re.I)
HTML_TAG_PATTERN = re.compile(r"<[^>]+>")
HTML_ENTITY_PATTERN = re.compile(r"&(?:[a-zA-Z]+|#\d+);")
STOPWORDS = {
    "about",
    "after",
    "amp",
    "and",
    "article",
    "are",
    "as",
    "at",
    "but",
    "by",
    "can",
    "com",
    "comments",
    "for",
    "from",
    "full",
    "gets",
    "going",
    "has",
    "have",
    "he",
    "for",
    "from",
    "have",
    "href",
    "how",
    "http",
    "https",
    "in",
    "into",
    "is",
    "item",
    "items",
    "just",
    "it",
    "its",
    "minutes",
    "my",
    "new",
    "now",
    "of",
    "on",
    "our",
    "out",
    "over",
    "points",
    "she",
    "that",
    "the",
    "this",
    "to",
    "with",
    "what",
    "when",
    "where",
    "who",
    "will",
    "we",
    "was",
    "were",
    "your",
    "url",
    "video",
    "news",
    "today",
    "more",
    "www",
    "shorts",
}


def expand_path(value: str) -> Path:
    return Path(value).expanduser().resolve()


def extract_hashtags(*parts: str) -> list[str]:
    seen: set[str] = set()
    hashtags: list[str] = []
    for part in parts:
        for match in HASHTAG_PATTERN.findall(part or ""):
            tag = match.strip()
            key = tag.casefold()
            if tag and key not in seen:
                seen.add(key)
                hashtags.append(tag)
    return hashtags


def clean_text(text: str) -> str:
    cleaned = URL_PATTERN.sub(" ", text or "")
    cleaned = HTML_TAG_PATTERN.sub(" ", cleaned)
    cleaned = HTML_ENTITY_PATTERN.sub(" ", cleaned)
    return re.sub(r"\s+", " ", cleaned).strip()


def tokenize_text(text: str) -> list[str]:
    tokens: list[str] = []
    for token in WORD_PATTERN.findall(clean_text(text)):
        lowered = token.casefold()
        if len(lowered) < 2 or lowered in STOPWORDS:
            continue
        tokens.append(token)
    return tokens


def extract_keywords(title: str, description: str, hashtags: list[str], limit: int = 8) -> list[str]:
    counter: Counter[str] = Counter()
    for token in tokenize_text(f"{clean_text(title)} {clean_text(description)}"):
        counter[token] += 1
    for hashtag in hashtags:
        counter[hashtag] += 2
    return [word for word, _ in counter.most_common(limit)]


def detect_language(text: str) -> str:
    if re.search(r"[가-힣]", text or ""):
        return "ko"
    if re.search(r"[A-Za-z]", text or ""):
        return "en"
    return "und"


def infer_category(text: str, configured_categories: list[str] | None = None) -> str:
    haystack = (text or "").casefold()
    if "ai" in haystack or "tech" in haystack or "software" in haystack:
        return "tech"
    if "market" in haystack or "stock" in haystack or "crypto" in haystack:
        return "finance"
    if "food" in haystack or "recipe" in haystack or "cooking" in haystack:
        return "food"
    if "style" in haystack or "fashion" in haystack or "interior" in haystack:
        return "lifestyle"
    if configured_categories:
        return configured_categories[0]
    return "general"


def compute_trend_score(metrics: dict[str, object]) -> float:
    numeric_total = 0.0
    for key in ("views", "likes", "comments", "score", "ups", "mentions", "ratio"):
        value = metrics.get(key)
        if isinstance(value, (int, float)):
            numeric_total += float(value)
    if numeric_total <= 0:
        return 15.0
    return round(min(100.0, math.log10(numeric_total + 1.0) * 22.0), 2)


def parse_compact_number(text: str | None) -> int | None:
    if not text:
        return None
    cleaned = text.replace(",", "").strip().upper()
    match = re.search(r"(\d+(?:\.\d+)?)\s*([KMB])?", cleaned)
    if not match:
        digits = re.search(r"\d+", cleaned)
        return int(digits.group(0)) if digits else None
    value = float(match.group(1))
    suffix = match.group(2)
    multiplier = {"K": 1_000, "M": 1_000_000, "B": 1_000_000_000}.get(suffix, 1)
    return int(value * multiplier)


def compact_join(values: list[str], fallback: str = "-") -> str:
    cleaned = [value for value in values if value]
    return ", ".join(cleaned) if cleaned else fallback
