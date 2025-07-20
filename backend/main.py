from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import StreamingResponse, JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from PyPDF2 import PdfReader, PdfWriter
import io, re, zipfile, csv, os
from datetime import datetime
from typing import List
import smtplib

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# serve your frontend assets
app.mount("/static", StaticFiles(directory="backend/static"), name="static")

LOG_FILE = "usage_log.csv"
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w", newline="") as f:
        csv.writer(f).writerow(["Timestamp","Email","Endpoint","IP","Count"])

def log_usage(email, endpoint, ip, count):
    with open(LOG_FILE, "a", newline="") as f:
        csv.writer(f).writerow([datetime.utcnow().isoformat(), email, endpoint, ip, count])

def extract_toc_entries(pages):
    text = "".join(p.extract_text() or "" for p in pages)
    pattern = re.compile(r"#\d+:\s+(.*?):\s+(.*?Checklist).*?(\d+)", re.DOTALL)
    return [(int(pg)-1, f"{t1.strip()} - {t2.strip()}", pg) for t1,t2,pg in pattern.findall(text)]

def split_pdf(files: List[UploadFile]):
    readers = [PdfReader(f.file) for f in files]
    pages = [p for r in readers for p in r.pages]
    toc = []
    for r in readers:
        subset = r.pages[1:6] if len(r.pages)>5 else r.pages[1:]
        toc += extract_toc_entries(subset)
    if not toc:
        return None
    ranges = []
    for i,(start,name,pg) in enumerate(toc):
        end = toc[i+1][0] if i+1<len(toc) else len(pages)
        ranges.append((start,end,name,pg))
    buf = io.BytesIO()
    with zipfile.ZipFile(buf,"w") as z:
        manifest=[]
        for s,e,name,pg in ranges:
            w = PdfWriter()
            for p in pages[s:e]:
                w.add_page(p)
            tmp = io.BytesIO()
            w.write(tmp); tmp.seek(0)
            fn = re.sub(r'[\\/*?:"<>|]','_',name)+".pdf"
            z.writestr(fn, tmp.read())
            manifest.append({"Checklist":name,"Page":pg,"File":fn})
    buf.seek(0)
    return buf, manifest, len(ranges), toc[0][1]

@app.post("/upload")
async def upload(request: Request,
                 files: List[UploadFile] = File(...),
                 email: str = Form(...)):
    result = split_pdf(files)
    if not result:
        return JSONResponse(422, {"error":"No checklists found"})
    buf, manifest, count, prefix = result
    log_usage(email,"/upload", request.client.host, count)
    fn = f"{prefix.split()[0]}_chk_{datetime.utcnow():%Y%m%d}.zip"
    return StreamingResponse(buf, media_type="application/zip",
                             headers={"Content-Disposition":f"attachment; filename={fn}"})

@app.get("/")
async def landing():
    html = open("backend/static/index.html").read()
    return HTMLResponse(html)

@app.get("/acc-tool")
async def acc_tool():
    html = open("backend/static/acc_tool.html").read()
    return HTMLResponse(html)

@app.get("/bim-tool")
async def bim_tool():
    html = open("backend/static/bim_tool.html").read()
    return HTMLResponse(html)

@app.post("/contact")
async def contact(name: str = Form(...),
                  email: str = Form(...),
                  message: str = Form(...)):
    # Simple console log (or hook up SMTP here)
    print(f"[Contact] {name} <{email}>: {message}")
    return JSONResponse({"success": True})
