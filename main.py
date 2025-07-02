from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import JSONResponse
import pandas as pd
import os
from email_utils import send_email

app = FastAPI()

@app.post("/send-emails/")
async def send_bulk_emails(
    file: UploadFile,
    sender_email: str = Form(...),
    app_password: str = Form(...),
    subject: str = Form(...),
    body: str = Form(...)
):
    file_location = f"uploads/{file.filename}"
    with open(file_location, "wb+") as f:
        f.write(await file.read())

    try:
        df = pd.read_excel(file_location)
        email_list = df['Email'].dropna().tolist()
    except:
        return JSONResponse(status_code=400, content={"error": "Invalid Excel file"})

    results = []
    for recipient in email_list:
        status = send_email(sender_email, app_password, recipient, subject, body)
        results.append({ "email": recipient, "status": "Sent" if status else "Failed" })

    os.remove(file_location)
    return { "results": results }
