import os
import json

from .services.sqlite_store import SQLiteStore
from .services.file_processor import FileProcessor
from .services.excel_export import generate_excel_from_sqlite
from .types import AnalyzeResult, AnalyzeStatus


class TextAnalyzer:
	def __init__(self, upload_dir: str, result_dir: str):
		self.upload_dir = upload_dir
		self.result_dir = result_dir
		self.processor = FileProcessor()

	def get_result(self, task_id: str) -> AnalyzeResult:
		paths = {
			AnalyzeStatus.COMPLETED: self.get_result_path(task_id),
			AnalyzeStatus.ERROR: self.get_error_path(task_id),
			AnalyzeStatus.PROCESSING: self.get_upload_path(task_id),
		}

		for status, path in paths.items():
			if os.path.exists(path):
				return AnalyzeResult(status, path)

		return AnalyzeResult(AnalyzeStatus.NOT_FOUND)

	def execute(self, task_id: str) -> str:
		try:
			with SQLiteStore() as store:
				with open(self.get_upload_path(task_id), "rb") as f:
					self.processor.process(store, f)

				os.makedirs(self.result_dir, exist_ok=True)
				excel_path = self.get_result_path(task_id)
				generate_excel_from_sqlite(store, excel_path)
				return excel_path

		except Exception as e:
			error_path = self.get_error_path(task_id)
			with open(error_path, "w") as f:
				json.dump({"error": str(e)}, f)
			return error_path

	def get_result_path(self, task_id: str) -> str:
		return f"{self.result_dir}/{task_id}.xlsx"

	def get_upload_path(self, task_id: str) -> str:
		return f"{self.upload_dir}/{task_id}.txt"

	def get_error_path(self, task_id: str) -> str:
		return f"{self.result_dir}/{task_id}_error.json"
