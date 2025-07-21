from fastapi import FastAPI, UploadFile, Form, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import List
import zipfile

app = FastAPI()
app.mount("/static", StaticFiles(directory="backend/static"), name="static")
templates = Jinja2Templates(directory="backend/templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/acc", response_class=HTMLResponse)
async def acc(request: Request):
    return templates.TemplateResponse("acc.html", {"request": request})

@app.get("/bim", response_class=HTMLResponse)
async def bim(request: Request):
    return templates.TemplateResponse("bim.html", {"request": request})

@app.get("/contact", response_class=HTMLResponse)
async def contact_get(request: Request):
    return templates.TemplateResponse("contact.html", {"request": request})

@app.post("/contact")
async def contact_post(name: str = Form(...), email: str = Form(...), message: str = Form(...)):
    print(f"Contact form: {name}, {email}, {message}")
    return {"status": "received"}

@app.post("/process-acc")
async def process_acc(files: List[UploadFile], output_name: str = Form("acc_processed")):
    output_zip = f"{output_name}.zip"
    with zipfile.ZipFile(output_zip, "w") as zipf:
        for file in files:
            contents = await file.read()
            zipf.writestr(file.filename, contents)
    return FileResponse(output_zip, media_type='application/zip', filename=output_zip)

@app.post("/process-bim")
async def process_bim(files: List[UploadFile], output_name: str = Form("bim_processed")):
    output_zip = f"{output_name}.zip"
    with zipfile.ZipFile(output_zip, "w") as zipf:
        for file in files:
            contents = await file.read()
            zipf.writestr(file.filename, contents)
    return FileResponse(output_zip, media_type='application/zip', filename=output_zip)