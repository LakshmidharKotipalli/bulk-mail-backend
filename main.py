from fastapi import FastAPI, UploadFile, Form, File
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

app = FastAPI()

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with frontend URL for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

email_logs = []

# Auto-detect SMTP server and port
def detect_smtp_config(email):
    domain = email.split("@")[1]
    if domain == "gmail.com":
        return "smtp.gmail.com", 587
    elif domain == "ganait.com":
        return "mail.ganait.com", 587
    else:
        return f"smtp.{domain}", 587

@app.post("/send-emails/")
async def send_bulk_emails(
    email: str = Form(...),
    password: str = Form(...),
    subject: str = Form(...),
    body: str = Form(...),
    file: UploadFile = File(...)
):
    # Parse file
    if file.filename.endswith(".csv"):
        df = pd.read_csv(file.file)
    elif file.filename.endswith((".xls", ".xlsx")):
        df = pd.read_excel(file.file)
    elif file.filename.endswith(".json"):
        df = pd.read_json(file.file)
    else:
        return {"error": "Unsupported file format"}

    if "email" not in df.columns or "name" not in df.columns:
        return {"error": "File must have 'email' and 'name' columns"}

    smtp_server, smtp_port = detect_smtp_config(email)

    # Connect to SMTP
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(email, password)
    except Exception as e:
        return {"error": f"SMTP login failed: {str(e)}"}

    success = 0
    failed = 0

    for _, row in df.iterrows():
        recipient = row["email"]
        name = row["name"]
        personalized_subject = subject.replace("$name", name)
        personalized_body = body.replace("$name", name)

        msg = MIMEMultipart()
        msg["From"] = email
        msg["To"] = recipient
        msg["Subject"] = personalized_subject
        msg.attach(MIMEText(personalized_body, "plain"))

        try:
            server.sendmail(email, recipient, msg.as_string())
            success += 1
            status = "Sent"
        except Exception as e:
            failed += 1
            status = f"Failed: {e}"

        email_logs.append({
            "email": recipient,
            "name": name,
            "status": status,
            "timestamp": datetime.utcnow().isoformat()
        })

    server.quit()
    return {"message": f"✅ Emails sent: {success}, ❌ Failed: {failed}"}

@app.get("/logs")
def get_logs():
    return email_logs
