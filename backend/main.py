from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import shutil, os, zipfile
from typing import List
import uuid

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.mount("/static", StaticFiles(directory="backend/static"), name="static")
templates = Jinja2Templates(directory="backend/templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/acc", response_class=HTMLResponse)
async def acc_page(request: Request):
    return templates.TemplateResponse("acc.html", {"request": request})

@app.get("/bim", response_class=HTMLResponse)
async def bim_page(request: Request):
    return templates.TemplateResponse("bim.html", {"request": request})

@app.get("/contact", response_class=HTMLResponse)
async def contact_page(request: Request):
    return templates.TemplateResponse("contact.html", {"request": request})

@app.post("/upload/acc")
async def upload_acc(files: List[UploadFile] = File(...)):
    output_dir = Path("backend/static/acc_output")
    output_dir.mkdir(parents=True, exist_ok=True)
    zip_path = output_dir / f"acc_result_{uuid.uuid4().hex}.zip"

    with zipfile.ZipFile(zip_path, "w") as zipf:
        for file in files:
            file_path = output_dir / file.filename
            with open(file_path, "wb") as f:
                shutil.copyfileobj(file.file, f)
            zipf.write(file_path, arcname=file.filename)

    return FileResponse(zip_path, media_type='application/zip', filename=zip_path.name)

@app.post("/upload/bim")
async def upload_bim(files: List[UploadFile] = File(...)):
    output_dir = Path("backend/static/bim_output")
    output_dir.mkdir(parents=True, exist_ok=True)
    zip_path = output_dir / f"bim_result_{uuid.uuid4().hex}.zip"

    with zipfile.ZipFile(zip_path, "w") as zipf:
        for file in files:
            file_path = output_dir / file.filename
            with open(file_path, "wb") as f:
                shutil.copyfileobj(file.file, f)
            zipf.write(file_path, arcname=file.filename)

    return FileResponse(zip_path, media_type='application/zip', filename=zip_path.name)
