from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date


@dataclass
class Resource:
    url: str
    title: str
    description: str | None = None
    rough_date: date | None = None
    issue_number: int | None = None


class BaseScraper(ABC):
    @abstractmethod
    def fetch(self, count: int = 1):
        """Yield Resource objects."""
        ...
