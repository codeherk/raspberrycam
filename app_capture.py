import os
import boto3
from datetime import datetime

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QLabel, QHBoxLayout, QPushButton, QVBoxLayout, QApplication, QWidget, QGridLayout

from picamera2.previews.qt import QGlPicamera2
from picamera2 import Picamera2

# 4056x3040 camera dimension
# 2028x1520
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
now = None

def post_callback(request):
    t = ''.join("{}: {}\n".format(k, v) for k, v in request.get_metadata().items())
    print(t)
    # label.setText(t)

def save_to_s3(filename, path):
    s3 = boto3.resource('s3')
    BUCKET = "codeherk-picam"

    s3.Bucket(BUCKET).upload_file(filename, path)

    print(f"Saved {filename} to S3!")

def on_button_clicked():
    global now
    button.setEnabled(False)
    now = datetime.now() # current date and time
    d = now.strftime("%m-%d-%Y_%H-%M-%S")
    filename = f"{d}.jpg"

    picam2.switch_mode_and_capture_file(capture_config, filename, wait=False, signal_function=qpicamera2.signal_done)

# Renable button and save image to S3 bucket
def capture_done():
    button.setEnabled(True)
    d = now.strftime("%m-%d-%Y_%H-%M-%S")
    filename = f"{d}.jpg"
    cwd = os.getcwd()
    print(f"current directory {cwd}")
    print(f"Image {filename} saved to {cwd}/!")

    save_to_s3(f"{cwd}/{filename}",f"{now.strftime('%m-%d-%Y')}/{filename}")


picam2 = Picamera2()
picam2.post_callback = post_callback
picam2.configure(picam2.create_preview_configuration(main={"size": (SCREEN_WIDTH, SCREEN_HEIGHT)}))
capture_config = picam2.create_still_configuration(main={"size": (SCREEN_WIDTH, SCREEN_HEIGHT)})

app = QApplication([])

qpicamera2 = QGlPicamera2(picam2, width=SCREEN_WIDTH, height=SCREEN_HEIGHT)
button = QPushButton("CAPTURE")
# label = QLabel()
window = QWidget()
qpicamera2.done_signal.connect(capture_done)
button.clicked.connect(on_button_clicked)

# label.setFixedWidth(400)
# label.setAlignment(QtCore.Qt.AlignTop)

layout = QGridLayout()

# layout.addWidget(label)
layout.addWidget(qpicamera2, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
button.setFixedHeight(125)
button.setStyleSheet("background-color: rgba(255, 255, 255, 0.2); border: none; color: black; font-weight: bold;")
layout.addWidget(button, SCREEN_HEIGHT-75, 350, 100, 125)
layout.setContentsMargins(0, 0, 0, 0)

window.setWindowTitle("Qt Picamera2 App")
window.resize(SCREEN_WIDTH, SCREEN_HEIGHT)
window.setLayout(layout)

picam2.start()
window.show()
app.exec()
