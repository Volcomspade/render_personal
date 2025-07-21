# backend/main.py

from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
import shutil
import zipfile
import os
import uuid

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")

@app.get("/", response_class=HTMLResponse)
async def landing(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/acc", response_class=HTMLResponse)
async def acc_tool(request: Request):
    return templates.TemplateResponse("acc.html", {"request": request})

@app.post("/process-acc")
async def process_acc(request: Request, files: list[UploadFile] = File(...)):
    zip_filename = f"acc_output_{uuid.uuid4().hex[:8]}.zip"
    zip_path = UPLOAD_DIR / zip_filename

    with zipfile.ZipFile(zip_path, "w") as zipf:
        for f in files:
            content = await f.read()
            filepath = UPLOAD_DIR / f.filename
            filepath.write_bytes(content)
            zipf.write(filepath, f.filename)
            filepath.unlink()  # clean up individual files

    return FileResponse(zip_path, filename=zip_filename, media_type='application/zip')

@app.get("/bim", response_class=HTMLResponse)
async def bim_tool(request: Request):
    return templates.TemplateResponse("bim.html", {"request": request})

@app.post("/process-bim")
async def process_bim(request: Request, files: list[UploadFile] = File(...)):
    zip_filename = f"bim_output_{uuid.uuid4().hex[:8]}.zip"
    zip_path = UPLOAD_DIR / zip_filename

    with zipfile.ZipFile(zip_path, "w") as zipf:
        for f in files:
            content = await f.read()
            filepath = UPLOAD_DIR / f.filename
            filepath.write_bytes(content)
            zipf.write(filepath, f.filename)
            filepath.unlink()

    return FileResponse(zip_path, filename=zip_filename, media_type='application/zip')

@app.get("/contact", response_class=HTMLResponse)
async def contact_page(request: Request):
    return templates.TemplateResponse("contact.html", {"request": request})
