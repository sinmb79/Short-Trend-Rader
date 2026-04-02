from __future__ import annotations

from abc import ABC, abstractmethod

import aiohttp

from trend_radar.config.schema import AppConfig
from trend_radar.models import CollectorResult


class BaseCollector(ABC):
    name: str

    @abstractmethod
    async def collect(self, config: AppConfig, session: aiohttp.ClientSession) -> CollectorResult:
        """Collect trend items for a single platform."""

    @abstractmethod
    def is_available(self) -> bool:
        """Return whether the collector can run in the current environment."""
