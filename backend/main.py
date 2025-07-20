from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from PyPDF2 import PdfReader, PdfWriter
import io, zipfile, csv, os
from datetime import datetime
from typing import List

app = FastAPI()

# enable CORS so AJAX form posts work
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# mount static files and templates
app.mount("/static", StaticFiles(directory="backend/static"), name="static")
templates = Jinja2Templates(directory="backend/templates")

LOG_FILE = "usage_log.csv"
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "Email", "Endpoint", "IP", "Count"])

def log_usage(email: str, endpoint: str, ip: str, count: int):
    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now().isoformat(), email, endpoint, ip, count])

@app.get("/", response_class=HTMLResponse)
def landing(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/acc", response_class=HTMLResponse)
def acc_page(request: Request):
    return templates.TemplateResponse("acc_tool.html", {"request": request})

@app.get("/bim", response_class=HTMLResponse)
def bim_page(request: Request):
    return templates.TemplateResponse("bim_tool.html", {"request": request})

def split_pdf(file_bytes: bytes, split_points: List[int]) -> io.BytesIO:
    reader = PdfReader(io.BytesIO(file_bytes))
    writer = PdfWriter()
    for p in split_points:
        if 0 <= p < len(reader.pages):
            writer.add_page(reader.pages[p])
    out = io.BytesIO()
    writer.write(out)
    out.seek(0)
    return out

def make_zip(parts: dict) -> io.BytesIO:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        for name, pdf_bytes in parts.items():
            z.writestr(name, pdf_bytes.getvalue())
    buf.seek(0)
    return buf

@app.post("/upload")
async def acc_upload(
    file: UploadFile = File(...),
    email: str = Form(...),
    pages: str = Form(...)
):
    pts = [int(p) for p in pages.split(",") if p.strip().isdigit()]
    data = await file.read()
    part = split_pdf(data, pts)
    bundle = make_zip({f"chunk_{p}.pdf": part for p in pts})
    log_usage(email, "/upload", file.client.host, len(pts))
    return StreamingResponse(bundle, media_type="application/zip", headers={
        "Content-Disposition": 'attachment; filename="acc_splits.zip"'
    })

@app.post("/bim-upload")
async def bim_upload(
    file: UploadFile = File(...),
    email: str = Form(...),
    pages: str = Form(...)
):
    # identical logic for BIM
    return await acc_upload(file, email, pages)
