from fastapi import FastAPI
from api.report import router as report_router
from contextlib import asynccontextmanager
import os
import asyncio

from features.text_analyzer import analyzer


async def cleanup_old_files():
	import time
	from pathlib import Path

	while True:
		now = time.time()
		max_age = 24 * 3600

		for folder in [analyzer.upload_dir, analyzer.result_dir]:
			for file_path in Path(folder).glob("*"):
				if file_path.is_file() and (now - file_path.stat().st_mtime) > max_age:
					file_path.unlink()

		await asyncio.sleep(3600)


@asynccontextmanager
async def lifespan(app: FastAPI):
	# startup
	os.makedirs(analyzer.upload_dir, exist_ok=True)
	os.makedirs(analyzer.result_dir, exist_ok=True)

	cleanup_task = asyncio.create_task(cleanup_old_files())
	yield

	# shutdown
	cleanup_task.cancel()
	await asyncio.sleep(1)


app = FastAPI(lifespan=lifespan)
app.include_router(report_router, prefix="/public/report")
