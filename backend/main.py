from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
from zipfile import ZipFile
from pathlib import Path
import uuid

app = FastAPI()

app.mount("/static", StaticFiles(directory="backend/static"), name="static")
templates = Jinja2Templates(directory="backend/templates")

UPLOAD_DIR = "uploads"
Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)

@app.get("/", response_class=HTMLResponse)
async def homepage(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/acc", response_class=HTMLResponse)
async def acc_tool(request: Request):
    return templates.TemplateResponse("acc.html", {"request": request})

@app.get("/bim", response_class=HTMLResponse)
async def bim_tool(request: Request):
    return templates.TemplateResponse("bim.html", {"request": request})

@app.get("/contact", response_class=HTMLResponse)
async def contact(request: Request):
    return templates.TemplateResponse("contact.html", {"request": request})

@app.post("/process_acc")
async def process_acc(files: list[UploadFile] = File(...)):
    session_dir = os.path.join(UPLOAD_DIR, str(uuid.uuid4()))
    os.makedirs(session_dir, exist_ok=True)
    zip_name = os.path.join(session_dir, "acc_output.zip")

    with ZipFile(zip_name, "w") as zipf:
        for file in files:
            contents = await file.read()
            filepath = os.path.join(session_dir, file.filename)
            with open(filepath, "wb") as f:
                f.write(contents)
            zipf.write(filepath, arcname=file.filename)

    return FileResponse(zip_name, filename="acc_output.zip")