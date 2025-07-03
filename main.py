from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import io
import smtplib
from email.message import EmailMessage

app = FastAPI()

# CORS setup for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app = FastAPI()

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
    try:
        contents = await file.read()
        df = pd.read_excel(io.BytesIO(contents))
        email_list = df.iloc[:, 0].dropna().tolist()

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(sender_email, app_password)
            for recipient in email_list:
                msg = EmailMessage()
                msg["Subject"] = subject
                msg["From"] = sender_email
                msg["To"] = recipient
                msg.set_content(body)
                smtp.send_message(msg)

        return {"message": "Emails sent successfully!"}

    except Exception as e:
        return {"error": str(e)}
