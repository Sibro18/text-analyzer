import re
from functools import lru_cache
from pymorphy3 import MorphAnalyzer
from typing import Iterable

from ..types import LineStats
from ..interfaces import IStore

_morph = MorphAnalyzer()
WORD_PATTERN = re.compile(r"[а-яёa-z0-9-]+", re.IGNORECASE)
NORM_PATTERN = r"[^а-яёa-z0-9-]"


class FileProcessor:
	def process(self, store: IStore, lines: Iterable[bytes]) -> None:
		totals = {}

		for i, raw in enumerate(lines):
			stats = self.__process_line(raw)

			store.append_line_stats(LineStats(i, stats))

			for w, cnt in stats.items():
				totals[w] = totals.get(w, 0) + cnt

		store.append_totals(totals)

	@lru_cache(maxsize=100_000)
	def __normalize_word(self, word: str) -> str:
		clean = re.sub(NORM_PATTERN, "", word.lower())

		if not clean or len(clean) > 50:
			return ""

		try:
			return _morph.parse(clean)[0].normal_form
		except Exception:
			return clean

	def __process_line(self, line: bytes) -> dict[str, int]:
		try:
			text = line.decode("utf-8", errors="ignore").lower()
		except UnicodeDecodeError:
			return {}

		words = WORD_PATTERN.findall(text)
		stats = {}

		for w in words:
			lemma = self.__normalize_word(w)
			if lemma and len(lemma) > 1:
				stats[lemma] = stats.get(lemma, 0) + 1

		return stats
