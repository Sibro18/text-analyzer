import os


class Config:
	class TextAnalyzer:
		UPLOAD_DIR = os.getenv("UPLOAD_DIR", "files/uploads")
		RESULT_DIR = os.getenv("RESULT_DIR", "files/results")

	CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
	CELERY_RESULT_BACKEND = os.getenv(
		"CELERY_RESULT_BACKEND", "redis://localhost:6379/0"
	)
