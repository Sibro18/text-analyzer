from celery import Celery
from features.text_analyzer import analyzer
from core.config import Config


celery_app = Celery(
	"worker",
	broker=Config.CELERY_BROKER_URL,
	backend=Config.CELERY_RESULT_BACKEND,
)


@celery_app.task
def process_file(task_id: str):
	analyzer.execute(task_id)
	return {"status": "done", "task_id": task_id}
