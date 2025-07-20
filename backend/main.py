import os
from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from PyPDF2 import PdfReader, PdfWriter

app = FastAPI()

BASE_DIR = os.path.dirname(__file__)

# 1) serve your CSS/JS/images
app.mount(
    "/static",
    StaticFiles(directory=os.path.join(BASE_DIR, "static")),
    name="static",
)

# 2) tell Jinja where your .html lives
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

@app.get("/")
async def landing_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# ACC tool routes
@app.get("/acc-tool")
async def acc_form(request: Request):
    return templates.TemplateResponse("acc_tool.html", {"request": request})

@app.post("/acc-tool")
async def acc_process(
    pdf_file: UploadFile = File(...),
    output_name: str = Form(...),
):
    reader = PdfReader(pdf_file.file)
    writer = PdfWriter()
    for p in reader.pages:
        writer.add_page(p)
    # Make sure outputs/ exists
    out_dir = os.path.join(BASE_DIR, "static", "outputs")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"{output_name}.pdf")
    with open(out_path, "wb") as f:
        writer.write(f)
    return FileResponse(out_path, media_type="application/pdf", filename=f"{output_name}.pdf")

# BIM tool routes (same pattern—swap in your real BIM logic)
@app.get("/bim-tool")
async def bim_form(request: Request):
    return templates.TemplateResponse("bim_tool.html", {"request": request})

@app.post("/bim-tool")
async def bim_process(
    pdf_file: UploadFile = File(...),
    output_name: str = Form(...),
):
    reader = PdfReader(pdf_file.file)
    writer = PdfWriter()
    for p in reader.pages:
        writer.add_page(p)
    out_dir = os.path.join(BASE_DIR, "static", "outputs")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"{output_name}.pdf")
    with open(out_path, "wb") as f:
        writer.write(f)
    return FileResponse(out_path, media_type="application/pdf", filename=f"{output_name}.pdf")
