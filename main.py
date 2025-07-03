from fastapi import FastAPI, UploadFile, Form, File
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = FastAPI()

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with your frontend domain for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/send-emails/")
async def send_bulk_emails(
    email: str = Form(...),
    password: str = Form(...),
    smtp_server: str = Form(...),
    smtp_port: int = Form(...),
    subject: str = Form(...),
    body: str = Form(...),
    file: UploadFile = File(...)
):
    # Load uploaded file into DataFrame
    if file.filename.endswith(".csv"):
        df = pd.read_csv(file.file)
    elif file.filename.endswith((".xls", ".xlsx")):
        df = pd.read_excel(file.file)
    elif file.filename.endswith(".json"):
        df = pd.read_json(file.file)
    else:
        return {"error": "Unsupported file type"}

    # Check required columns
    if "email" not in df.columns or "name" not in df.columns:
        return {"error": "File must contain 'email' and 'name' columns"}

    # Connect to SMTP
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(email, password)
    except Exception as e:
        return {"error": f"SMTP login failed: {str(e)}"}

    # Send emails
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
        except Exception:
            failed += 1

    server.quit()
    return {"message": f"Emails sent: {success}, Failed: {failed}"}
