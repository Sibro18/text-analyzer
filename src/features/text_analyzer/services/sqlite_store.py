import sqlite3
import json
import tempfile
import os
from typing import Optional

from ..types import LineStats
from ..interfaces import IStore


class SQLiteStore(IStore):
	def __init__(self, db_path: Optional[str] = None, batch_size: int = 1000):
		if db_path is None:
			fd, self.db_path = tempfile.mkstemp(suffix=".db", prefix="word_stats_")
			os.close(fd)
		else:
			self.db_path = db_path

		self.conn = None
		self.cursor = None
		self.__counter = 0
		self.batch_size = batch_size

	def _init_db(self):
		c = self.cursor

		c.execute("PRAGMA journal_mode=WAL")
		c.execute("PRAGMA synchronous=NORMAL")
		c.execute("PRAGMA cache_size=-10000")

		c.execute("""
			CREATE TABLE IF NOT EXISTS line_stats (
				line_number INTEGER PRIMARY KEY,
				stats_json TEXT NOT NULL
			)
		""")

		c.execute("""
				CREATE TABLE IF NOT EXISTS total_stats (
				word TEXT PRIMARY KEY,
				total INTEGER NOT NULL
			)
		""")

		self.conn.commit()

	def __enter__(self):
		self.conn = sqlite3.connect(self.db_path)
		self.conn.row_factory = sqlite3.Row
		self.cursor = self.conn.cursor()
		self._init_db()

		return self

	def __exit__(self, *args, **kwargs):
		if self.conn:
			self.conn.commit()
			self.conn.close()
		os.unlink(self.db_path)

	def append_line_stats(self, stats: LineStats) -> None:
		if not self.conn:
			raise Exception("SQLiteStore: connection does not exists")

		self.cursor.execute(
			"INSERT INTO line_stats (line_number, stats_json) VALUES (?, ?)",
			(stats.index, json.dumps(stats.data, ensure_ascii=False)),
		)

		self.__counter += 1
		if self.__counter % self.batch_size == 0:
			self.conn.commit()

	def append_totals(self, totals: dict[str, int]) -> None:
		if not self.conn:
			raise Exception("SQLiteStore: connection does not exists")

		self.cursor.executemany(
			"INSERT INTO total_stats (word, total) VALUES (?, ?)", list(totals.items())
		)
		self.conn.commit()

	def get_line_stats(self) -> list[dict[str, int]]:
		if not self.conn:
			raise Exception("SQLiteStore: connection does not exists")

		output = []
		for row in self.cursor.execute(
			"SELECT stats_json FROM line_stats ORDER BY line_number"
		):
			output.append(json.loads(row["stats_json"]))

		return output

	def get_totals(self) -> dict[str, int]:
		if not self.conn:
			raise Exception("SQLiteStore: connection does not exists")

		totals = {}

		for row in self.cursor.execute(
			"SELECT word, total FROM total_stats ORDER BY total DESC"
		):
			totals[row["word"]] = row["total"]

		return totals
