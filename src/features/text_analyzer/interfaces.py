from abc import ABC, abstractmethod
from .types import LineStats


class IStore(ABC):
	@abstractmethod
	def append_line_stats(stats: LineStats):
		pass

	@abstractmethod
	def append_totals(totals: dict[str, int]):
		pass

	@abstractmethod
	def get_line_stats(self) -> list[dict[str, int]]:
		pass

	@abstractmethod
	def get_totals(self) -> dict[str, int]:
		pass
