from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="backend/static")

@app.get("/", response_class=HTMLResponse)
async def landing_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/contact")
async def contact_form(name: str = Form(...), email: str = Form(...), message: str = Form(...)):
    print(f"Contact Form Submitted: {name}, {email}, {message}")
    return {"success": True}

@app.get("/acc-tool", response_class=HTMLResponse)
async def acc_tool(request: Request):
    return templates.TemplateResponse("acc_tool.html", {"request": request})

@app.get("/bim-tool", response_class=HTMLResponse)
async def bim_tool(request: Request):
    return templates.TemplateResponse("bim_tool.html", {"request": request})
