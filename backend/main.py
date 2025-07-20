from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import smtplib
from email.message import EmailMessage
import os

app = FastAPI()

# Enable CORS if needed (optional)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
async def root():
    return "<h1>Checklist Splitter API is running!</h1>"

@app.post("/contact")
async def send_email(
    name: str = Form(...),
    email: str = Form(...),
    message: str = Form(...)
):
    smtp_user = os.environ.get("SMTP_USER")
    smtp_pass = os.environ.get("SMTP_PASS")
    smtp_server = os.environ.get("SMTP_SERVER")
    smtp_port = int(os.environ.get("SMTP_PORT", 587))
    contact_email = os.environ.get("CONTACT_EMAIL")

    if not all([smtp_user, smtp_pass, smtp_server, contact_email]):
        return {"error": "SMTP configuration incomplete."}

    try:
        msg = EmailMessage()
        msg["Subject"] = f"New Contact from {name}"
        msg["From"] = smtp_user
        msg["To"] = contact_email
        msg.set_content(f"From: {name} <{email}>\n\n{message}")

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)

        return {"status": "success", "message": "Email sent successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
