import cv2
import time
import sys
import base64

sys.path.append("/home/mulip-guest/LeRobot/lerobot/custom_brains")
from camera_readers import CameraReader

print("Starting webcam...")
webcam_url = "rtsp://10.243.126.188:8080/h264_ulaw.sdp"
webcam_cap = cv2.VideoCapture(webcam_url)
webcam_reader = CameraReader(webcam_cap)
webcam_reader.start()

while webcam_reader.frame is None:
    print("\rWaiting... on webcam")
    time.sleep(0.01)

def get_latest():
    print(f"Getting latest!")
    frame = webcam_reader.frame
    print(f"Latest got!")
    return frame_to_data_url(frame)

def frame_to_data_url(frame):
    # Encode to PNG in memory
    success, encoded = cv2.imencode(".png", frame)
    if not success:
        raise ValueError("Failed to encode frame")

    # Convert to base64 string
    b64_bytes = base64.b64encode(encoded.tobytes())
    b64_string = b64_bytes.decode("utf-8")

    # Create data URL
    return f"data:image/png;base64,{b64_string}"