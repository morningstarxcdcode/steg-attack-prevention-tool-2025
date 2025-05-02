import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QTextEdit
from PyQt5.QtCore import QThread, pyqtSignal
import cv2
from PIL import Image
import numpy as np
import logging
from plyer import notification
from sklearn.ensemble import RandomForestClassifier
import joblib
import os

# Load or train model (same as main.py)
MODEL_PATH = 'steg_model.joblib'

def train_dummy_model():
    X = [
        [0.1, 0.1, 0.1],
        [0.5, 0.5, 0.5],
        [0.2, 0.2, 0.2],
        [0.6, 0.6, 0.6]
    ]
    y = [0, 1, 0, 1]
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
    for channel in range(3):
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

class CameraThread(QThread):
    alert_signal = pyqtSignal(str)
    frame_signal = pyqtSignal(np.ndarray)

    def __init__(self):
        super().__init__()
        self.running = False

    def run(self):
        self.running = True
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            self.alert_signal.emit("Error: Could not open camera.")
            return

        while self.running:
            ret, frame = cap.read()
            if not ret:
                self.alert_signal.emit("Failed to grab frame.")
                break

            image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            features = extract_lsb_ratios(image)
            prediction = model.predict([features])[0]

            if prediction == 1:
                alert_msg = "[ALERT] Potential steganography detected in camera frame!"
                logging.info(alert_msg)
                self.alert_signal.emit(alert_msg)
                notify_user(alert_msg)

            self.frame_signal.emit(frame)

        cap.release()

    def stop(self):
        self.running = False
        self.wait()

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Steganography Attack Prevention Tool")
        self.setGeometry(100, 100, 640, 480)

        self.layout = QVBoxLayout()

        self.status_label = QLabel("Status: Idle")
        self.layout.addWidget(self.status_label)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.layout.addWidget(self.log_text)

        self.start_button = QPushButton("Start Camera Scan")
        self.start_button.clicked.connect(self.start_scan)
        self.layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop Camera Scan")
        self.stop_button.clicked.connect(self.stop_scan)
        self.stop_button.setEnabled(False)
        self.layout.addWidget(self.stop_button)

        self.setLayout(self.layout)

        self.camera_thread = CameraThread()
        self.camera_thread.alert_signal.connect(self.handle_alert)
        self.camera_thread.frame_signal.connect(self.update_frame)

    def start_scan(self):
        self.camera_thread.start()
        self.status_label.setText("Status: Scanning...")
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

    def stop_scan(self):
        self.camera_thread.stop()
        self.status_label.setText("Status: Idle")
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def handle_alert(self, message):
        self.log_text.append(message)

    def update_frame(self, frame):
        # For simplicity, not displaying video feed in GUI now
        pass

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
