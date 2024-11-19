from flask import Flask, Response
import cv2
from deepface import DeepFace
import pandas as pd
from datetime import datetime
import os

# Initialize the Flask app
app = Flask(__name__)

# Excel file to store emotions and their timestamps
excel_file = "emotions_log.xlsx"

# Create an Excel file if it doesn't exist
def create_excel_file():
    if not os.path.exists(excel_file):
        df = pd.DataFrame(columns=["Timestamp", "Emotion"])
        df.to_excel(excel_file, index=False)

create_excel_file()

# Load face cascade classifier
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Video feed with emotion detection and logging
def generate_frames():
    cap = cv2.VideoCapture(0)  # 0 for the default webcam

    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            # Convert frame to grayscale
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            rgb_frame = cv2.cvtColor(gray_frame, cv2.COLOR_GRAY2RGB)

            # Detect faces in the frame
            faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

            for (x, y, w, h) in faces:
                # Extract the face ROI (Region of Interest)
                face_roi = rgb_frame[y:y + h, x:x + w]

                try:
                    # Perform emotion analysis on the face ROI
                    result = DeepFace.analyze(face_roi, actions=['emotion'], enforce_detection=False)
                    emotion = result[0]['dominant_emotion']

                    # Log emotion and timestamp in Excel
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Append data to the Excel file
                    existing_data = pd.read_excel(excel_file)
                    new_data = pd.DataFrame([[timestamp, emotion]], columns=["Timestamp", "Emotion"])
                    updated_data = pd.concat([existing_data, new_data], ignore_index=True)
                    updated_data.to_excel(excel_file, index=False)

                    # Draw rectangle around the face and label it with the emotion
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                    cv2.putText(frame, emotion, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
                except Exception as e:
                    print(f"Error analyzing emotion: {e}")

            # Encode the frame to be sent via HTTP
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    """Endpoint for streaming real-time video feed."""
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
