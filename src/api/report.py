from fastapi import APIRouter, UploadFile, File, BackgroundTasks
from fastapi.responses import FileResponse
from uuid import uuid4


from src.features.text_analyzer import analyzer
from src.apps.celery_app import process_file
from src.features.text_analyzer.types import AnalyzeStatus

router = APIRouter()


async def save_and_process(upload_path: str, file: UploadFile, task_id: str):
	import aiofiles

	async with aiofiles.open(upload_path, "wb") as f:
		while True:
			chunk = await file.read(64 * 1024)
			if not chunk:
				break
			await f.write(chunk)
	process_file.delay(task_id)


@router.post("/export")
async def export_report(
	file: UploadFile = File(...), background_tasks: BackgroundTasks = None
):
	task_id = str(uuid4())
	background_tasks.add_task(
		save_and_process, analyzer.get_upload_path(task_id), file, task_id
	)
	return {"task_id": task_id, "status": "processing"}


@router.get("/result/{task_id}")
async def get_excel(task_id: str):
	result = analyzer.get_result(task_id)

	def error_handler(file_path):
		with open(file_path, "r", encoding="utf-8") as f:
			return {"status": "error", "error": f.read()}

	def completed_handler(file_path, task_id):
		return FileResponse(
			path=file_path,
			filename=f"result_{task_id}.xlsx",
			media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
		)

	return_dict = {
		AnalyzeStatus.COMPLETED: lambda: completed_handler(result.path, task_id),
		AnalyzeStatus.ERROR: lambda: error_handler(result.path),
		AnalyzeStatus.PROCESSING: lambda: {"status": "processing"},
		AnalyzeStatus.NOT_FOUND: lambda: {"status": "not_found"},
	}

	return return_dict[result.status]()


@router.get("/status/{task_id}")
async def get_task_status(task_id: str):
	result = analyzer.get_result(task_id)
	return {"status": result.status}
