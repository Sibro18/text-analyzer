# services/excel_export.py

import openpyxl
from openpyxl.styles import Alignment, Font
from openpyxl.cell import WriteOnlyCell

from ..interfaces import IStore


def generate_excel_from_sqlite(store: IStore, excel_path: str):
	wb = openpyxl.Workbook(write_only=True)
	ws = wb.create_sheet("Word Statistics")

	header = ["Слово", "Всего", "По строкам"]
	header_row = []

	bold = Font(bold=True)
	center = Alignment(horizontal="center")

	for value in header:
		cell = WriteOnlyCell(ws, value=value)
		cell.font = bold
		cell.alignment = center
		header_row.append(cell)

	ws.append(header_row)

	totals = store.get_totals()
	line_stats = store.get_line_stats()

	for word, total in totals.items():
		per_line_counts = [ls.get(word, 0) for ls in line_stats]
		ws.append([word, total, ",".join(map(str, per_line_counts))])

	wb.save(excel_path)
