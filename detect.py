import cv2
import numpy as np
import requests  # <-- ADDED FOR SENDING ALERTS
from ultralytics import YOLO

# --- 1. Configuration ---
RTSP_URL = 0  # 0 for webcam, or your "rtsp://..." string
MODEL_PATH = 'best.pt'
CONF_THRESHOLD = 0.70
FRAME_COUNT_THRESHOLD = 3
FIRE_CLASS_IDS = [0, 1]  # 0='smoke', 1='fire'
FASTAPI_SERVER_URL = "http://127.0.0.1:8000/alert"

# --- 2. Initialization ---
print("Loading model...")
model = YOLO(MODEL_PATH)

print(f"Connecting to video stream ({RTSP_URL})...")
try:
    cap = cv2.VideoCapture(RTSP_URL)
    if not cap.isOpened():
        raise Exception("Cannot open video capture.")
    print("Video stream connected successfully.")
except Exception as e:
    print(f"--- ERROR: Failed to connect to video stream. ---")
    print(f"--- If using a webcam, is it in use by another app? ---")
    print(f"--- Error details: {e} ---")
    exit()

fire_detection_counter = 0
print("--- Starting fire detection loop (Press 'q' to quit) ---")

# --- 3. Main Processing Loop ---
while True:
    ret, frame = cap.read()
    if not ret:
        print("Stream ended or error.")
        break

    # --- 4. AI Model Inference ---
    results = model(frame, stream=True, verbose=False)

    found_high_conf_fire = False

    # --- 5. Process Results (Apply Logic) ---
    for result in results:
        boxes = result.boxes
        for box in boxes:
            confidence = box.conf[0]
            class_id = int(box.cls[0])

            if class_id in FIRE_CLASS_IDS and confidence >= CONF_THRESHOLD:
                found_high_conf_fire = True

                # --- (Optional) Draw a box on the frame ---
                # --- NEW, CORRECT LINE ---
                x1, y1, x2, y2 = np.array(box.xyxy[0], dtype=int)
                label = f"{model.names[class_id]}: {confidence:.2f}"
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                cv2.putText(frame, label, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                break  # Only need one detection per frame

    # --- 6. Implement "3+ Frames" Logic ---
    if found_high_conf_fire:
        fire_detection_counter += 1
    else:
        fire_detection_counter = 0  # Reset counter if no fire is found

    # --- 7. Trigger Alert ---
    if fire_detection_counter >= FRAME_COUNT_THRESHOLD:
        print(f"!!! ALERT: Fire detected for {fire_detection_counter} frames! Sending to server... !!!")
        try:
            # Send an HTTP POST request to your FastAPI server
            r = requests.post(FASTAPI_SERVER_URL)
            r.raise_for_status()  # Raise an exception if the server returns an error
            print("--- Alert successfully sent to server. ---")
        except requests.exceptions.ConnectionError:
            print("--- ERROR: Could not connect to FastAPI server. Is it running? ---")
        except Exception as e:
            print(f"--- ERROR: An unknown error occurred: {e} ---")

        # Reset counter after sending alert to avoid spamming
        fire_detection_counter = 0

    # --- (Optional) Display the video feed ---
    cv2.imshow("Fire Detection Stream", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# --- 8. Cleanup ---
cap.release()
cv2.destroyAllWindows()
print("--- Detection stopped. ---")