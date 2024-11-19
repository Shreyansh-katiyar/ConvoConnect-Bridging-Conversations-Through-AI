from flask import Flask, Response, request
import cv2
import pandas as pd
from nltk.sentiment import SentimentIntensityAnalyzer
from datetime import datetime

# Initialize the Flask app
app = Flask(__name__)

# Initialize Sentiment Analyzer
sia = SentimentIntensityAnalyzer()

# Excel file to store the responses and sentiment
excel_file = "interview_data.xlsx"

# Create a DataFrame to store responses and sentiment
def create_excel_file():
    if not pd.io.common.file_exists(excel_file):
        df = pd.DataFrame(columns=["Timestamp", "Response", "Sentiment", "Sentiment Score"])
        df.to_excel(excel_file, index=False)

create_excel_file()

# to show video in chatbot

def generate_frames():
    cap = cv2.VideoCapture(0)  # 0 for default webcam

    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/submit_answer', methods=["POST"])
def submit_answer():
    answer = request.form.get("answer")
    if answer:
        # Perform Sentiment Analysis
        sentiment = sia.polarity_scores(answer)
        sentiment_label = "Positive" if sentiment["compound"] >= 0.05 else "Negative" if sentiment["compound"] <= -0.05 else "Neutral"
        
        # Log the timestamp and response
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Store in Excel
        data = pd.DataFrame([[timestamp, answer, sentiment_label, sentiment["compound"]]], 
                            columns=["Timestamp", "Response", "Sentiment", "Sentiment Score"])
        data.to_excel(excel_file, index=False, header=False, mode='a')
        
        return "Answer submitted and sentiment analyzed!"
    return "No answer provided."

# JavaScript to detect tab-switching and alert the user
@app.route('/check_tab_switching')
def check_tab_switching():
    return '''
    <script>
        document.addEventListener('visibilitychange', function() {
            if (document.hidden) {
                alert("Warning: You have switched tabs. This is not allowed during the interview.");
            }
        });
    </script>
    '''

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
