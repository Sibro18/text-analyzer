from dataclasses import dataclass
from enum import Enum


class AnalyzeStatus(Enum):
	COMPLETED = "completed"
	ERROR = "error"
	PROCESSING = "processing"
	NOT_FOUND = "not found"


@dataclass()
class AnalyzeResult:
	status: AnalyzeStatus
	path: str | None = None


@dataclass()
class LineStats:
	index: int
	data: dict[str, int]
