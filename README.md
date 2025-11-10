# Real-Time Fire Detection and Alert System

This project uses a YOLOv8 model to detect fire and smoke from a live video stream. When a fire is confirmed, it sends an alert to a FastAPI server, which then triggers an email, SMS, and automated phone call via Twilio.

## Features
- **AI Model:** Fine-tuned YOLOv8 model for fire and smoke detection.
- **Detection Client:** `detect.py` (OpenCV) captures video and runs inference.
- **API Server:** `fastapi_server.py` receives alerts.
- **Alerts:** Sends notifications via Email (SMTP), SMS (Twilio), and Voice Call (Twilio).

## How to Run

### 1. Install Dependencies
```bash
pip install -r requirements.txt