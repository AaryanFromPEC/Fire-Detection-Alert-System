from fastapi import FastAPI
import uvicorn
import smtplib
import ssl
import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()
# --- Email Configuration ---
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "aaryanaggarwal2005@gmail.com"
RECEIVER_EMAIL = "aaryanaggarwal.bt23ece@pec.edu.in"

# --- Twilio Configuration ---
TO_PHONE_NUMBER = "+919915840484" # Phone number to alert

# --- Load all secrets from environment variables ---
EMAIL_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD")
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.environ.get("TWILIO_PHONE_NUMBER")
TWIML_BIN_URL = os.environ.get("TWIML_BIN_URL")  # <-- 1. ADD NEW VARIABLE
# --------------------------------------------------

app = FastAPI()

# (Your send_email() function stays here, unchanged)
def send_email():
    if not EMAIL_PASSWORD:
        print("--- ERROR: Cannot send email. Password is not set. ---")
        return
    # ... (rest of your email code is here) ...
    message = """\
Subject: !!! FIRE ALERT DETECTED !!!

A fire or smoke event has been confirmed by the AI detection system.
Please check the cameras immediately.
"""
    context = ssl.create_default_context()
    print("--- Connecting to Gmail server to send alert... ---")
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls(context=context)
        server.login(SENDER_EMAIL, EMAIL_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, message)
        server.quit()
        print("--- Email alert successfully sent! ---")
    except smtplib.SMTPException as e:
        print(f"--- ERROR: Failed to send email: {e} ---")
    except Exception as e:
        print(f"--- An unexpected error occurred: {e} ---")


# (Your send_sms() function stays here, unchanged)
def send_sms():
    if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER]):
        print("--- ERROR: Twilio credentials not set. Cannot send SMS. ---")
        return
    # ... (rest of your SMS code is here) ...
    print("--- Connecting to Twilio to send SMS... ---")
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body="!!! FIRE ALERT DETECTED !!! Check cameras immediately.",
            from_=TWILIO_PHONE_NUMBER,
            to=TO_PHONE_NUMBER
        )
        print(f"--- SMS alert successfully sent! (SID: {message.sid}) ---")
    except Exception as e:
        print(f"--- ERROR: Failed to send SMS: {e} ---")


# --- 2. ADD NEW MAKE_VOICE_CALL FUNCTION ---
def make_voice_call():
    """
    Uses Twilio to make an automated voice call.
    """
    if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER, TWIML_BIN_URL]):
        print("--- ERROR: Twilio credentials or TwiML URL not set. Cannot make call. ---")
        return

    print("--- Connecting to Twilio to make voice call... ---")
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        call = client.calls.create(
            url=TWIML_BIN_URL,  # <-- Tells Twilio what to say
            from_=TWILIO_PHONE_NUMBER,
            to=TO_PHONE_NUMBER
        )
        print(f"--- Voice call initiated! (SID: {call.sid}) ---")
    except Exception as e:
        print(f"--- ERROR: Failed to make voice call: {e} ---")
# ---------------------------------------------


@app.post("/alert")
async def receive_alert():
    """
    This endpoint triggers email, SMS, and a voice call.
    """
    print("-----------------------------------------")
    print("!!! ALERT RECEIVED FROM DETECTION SCRIPT !!!")
    print("--- Fire or smoke has been confirmed. ---")
    print("-----------------------------------------")
    
    # --- 3. CALL ALL THREE FUNCTIONS ---
    send_email()
    send_sms()
    make_voice_call()
    # ---------------------------------
    
    return {"status": "alert received, notifications triggered"}


if __name__ == "__main__":
    if not all([EMAIL_PASSWORD, TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER, TWIML_BIN_URL]):
        print("--- WARNING: One or more environment variables are missing! ---")
        print("--- Please set all 5 variables: GMAIL, TWILIO_SID, TWILIO_TOKEN, TWILIO_PHONE, and TWIML_BIN_URL ---")

    print("Starting FastAPI server on http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)