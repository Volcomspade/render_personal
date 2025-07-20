from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from PyPDF2 import PdfReader, PdfWriter
import io, re, zipfile, csv, os
from datetime import datetime
import pandas as pd
from typing import List

app = FastAPI()

# Allow frontend development access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

LOG_FILE = "usage_log.csv"
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "Email", "Endpoint", "IP Address", "Checklist Count"])

def log_usage(email: str, endpoint: str, ip: str, count: int):
    with open(LOG_FILE, mode='a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now().isoformat(), email, endpoint, ip, count])

def extract_toc_entries(pages):
    toc_text = "".join(page.extract_text() or "" for page in pages)
    pattern = re.compile(r"#\d+:\s+(.*?):\s+(.*?Checklist.*?)\.+\s+(\d+)", re.DOTALL)
    matches = pattern.findall(toc_text)
    entries = [(int(page_num) - 1, f"{title1.strip()} - {title2.strip()}", page_num) for title1, title2, page_num in matches]
    return entries

def split_pdf_by_toc(files: List[UploadFile]):
    readers = [PdfReader(f.file) for f in files]
    all_pages = [page for reader in readers for page in reader.pages]

    toc_entries = []
    for reader in readers:
        pages_to_check = reader.pages[1:6] if len(reader.pages) > 5 else reader.pages[1:]
        entries = extract_toc_entries(pages_to_check)
        if entries:
            toc_entries.extend(entries)

    if not toc_entries:
        return None, None, None, None

    split_ranges = []
    for i, (start, name, page_str) in enumerate(toc_entries):
        end = toc_entries[i + 1][0] if i + 1 < len(toc_entries) else len(all_pages)
        split_ranges.append((start, end, name, page_str))

    zip_buffer = io.BytesIO()
    manifest_data = []
    with zipfile.ZipFile(zip_buffer, "w") as zipf:
        for start, end, name, page_str in split_ranges:
            writer = PdfWriter()
            for page in all_pages[start:end]:
                writer.add_page(page)

            buffer = io.BytesIO()
            writer.write(buffer)
            buffer.seek(0)

            safe_name = re.sub(r'[\\/*?:"<>|]', "_", name.strip()) + ".pdf"
            zipf.writestr(safe_name, buffer.read())
            manifest_data.append({"Checklist Name": name, "Start Page": page_str, "File Name": safe_name})
    zip_buffer.seek(0)
    return zip_buffer, manifest_data, len(split_ranges), toc_entries[0][1] if toc_entries else "checklists"

def split_bim_checklist(files: List[UploadFile]):
    return split_pdf_by_toc(files)

@app.post("/upload")
async def upload_checklist(request: Request, files: List[UploadFile] = File(...), email: str = Form(...)):
    zip_data, manifest_data, count, project_prefix = split_pdf_by_toc(files)
    if not zip_data:
        return JSONResponse(status_code=422, content={"error": "No checklists found"})

    client_ip = request.client.host
    log_usage(email, "/upload", client_ip, count)

    today_str = datetime.now().strftime("%Y-%m-%d")
    zip_filename = f"{project_prefix.split()[0]}_checklists_{today_str}.zip"

    return StreamingResponse(zip_data, media_type="application/zip", headers={
        "Content-Disposition": f"attachment; filename={zip_filename}"
    })

@app.post("/bim-upload")
async def upload_bim_checklist(request: Request, files: List[UploadFile] = File(...), email: str = Form(...)):
    zip_data, manifest_data, count, project_prefix = split_bim_checklist(files)
    if not zip_data:
        return JSONResponse(status_code=422, content={"error": "No checklists found"})

    client_ip = request.client.host
    log_usage(email, "/bim-upload", client_ip, count)

    today_str = datetime.now().strftime("%Y-%m-%d")
    zip_filename = f"{project_prefix.split()[0]}_bim_checklists_{today_str}.zip"

    return StreamingResponse(zip_data, media_type="application/zip", headers={
        "Content-Disposition": f"attachment; filename={zip_filename}"
    })

@app.get("/usage")
async def get_usage_log():
    if not os.path.exists(LOG_FILE):
        return JSONResponse(content={"data": []})

    with open(LOG_FILE, mode='r') as f:
        reader = csv.DictReader(f)
        data = list(reader)

    return JSONResponse(content={"data": data})

@app.get("/")
async def landing_page():
    html = """
    <!DOCTYPE html>
    <html lang='en'>
    <head>
        <meta charset='UTF-8'>
        <meta name='viewport' content='width=device-width, initial-scale=1.0'>
        <title>Checklist Tools by Ryan Younker</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; padding: 2em; background: #f5f5f5; }
            h1 { color: #333; }
            p, a { color: #555; }
            .projects { margin-top: 2em; }
            .projects a { display: block; margin: 1em auto; text-decoration: none; color: #0066cc; font-weight: bold; }
            .footer { margin-top: 4em; font-size: 0.9em; color: #888; }
        </style>
    </head>
    <body>
        <h1>Checklist Splitter Tools</h1>
        <p>Hi, I'm Ryan Younker — a Quality Site Manager focused on Renewable Energy.<br>
        These tools are side projects I’ve been developing in my spare time to help simplify ACC Build and BIM checklist workflows.</p>
        <div class='projects'>
            <a href='/acc-tool'>ACC Checklist Splitter</a>
            <a href='/bim-tool'>BIM Checklist Splitter</a>
        </div>
        <p style='margin-top:2em;'>Connect with me on <a href='https://www.linkedin.com/in/ryan-younker-253365339/' target='_blank'>LinkedIn</a></p>
        <div class='footer'>
            <p><strong>Disclaimer:</strong> This site is under active development. Some errors may occur during use. Use at your own discretion.</p>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html, status_code=200)
