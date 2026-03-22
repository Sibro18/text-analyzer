from core.config import Config
from .analyzer import TextAnalyzer

analyzer = TextAnalyzer(
	upload_dir=Config.TextAnalyzer.UPLOAD_DIR,
	result_dir=Config.TextAnalyzer.RESULT_DIR,
)

__all__ = ["analyzer", "TextAnalyzer"]
