import cv2
import numpy as np
from PIL import Image
import threading
import time
import logging
from plyer import notification
from sklearn.ensemble import RandomForestClassifier
import joblib
import os

# Setup logging
logging.basicConfig(filename='detection.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Load or train a simple ML model for steganography detection (stub example)
MODEL_PATH = 'steg_model.joblib'

def train_dummy_model():
    # Dummy training data: features are ratio of LSB bits set in RGB channels
    X = [
        [0.1, 0.1, 0.1],  # clean images
        [0.5, 0.5, 0.5],  # stego images
        [0.2, 0.2, 0.2],
        [0.6, 0.6, 0.6]
    ]
    y = [0, 1, 0, 1]  # 0 = clean, 1 = stego
    clf = RandomForestClassifier()
    clf.fit(X, y)
    joblib.dump(clf, MODEL_PATH)
    return clf

if os.path.exists(MODEL_PATH):
    model = joblib.load(MODEL_PATH)
else:
    model = train_dummy_model()

def extract_lsb_ratios(image):
    pixels = np.array(image)
    ratios = []
    for channel in range(3):  # RGB channels
        channel_data = pixels[:, :, channel]
        lsb_bits = channel_data & 1
        ratio = np.sum(lsb_bits) / lsb_bits.size
        ratios.append(ratio)
    return ratios

def notify_user(message):
    notification.notify(
        title="Steganography Detection Alert",
        message=message,
        timeout=5
    )

def capture_and_scan():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    print("Starting camera capture. Press 'q' to quit.")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame.")
            break

        image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        features = extract_lsb_ratios(image)
        prediction = model.predict([features])[0]

        if prediction == 1:
            alert_msg = "[ALERT] Potential steganography detected in camera frame!"
            print(alert_msg)
            logging.info(alert_msg)
            notify_user(alert_msg)

        cv2.imshow('Camera Feed - Press q to quit', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def main():
    capture_and_scan()

if __name__ == "__main__":
    main()
