import socket
import struct
import numpy as np
import cv2
import threading
import base64
import sys
from pathlib import Path
import time


class ImageProcessorInitializingError(Exception):
    pass

# Factory function
def create(values):
    """Interfaces with custom_brains' camera_readers, in ways based on the type of each value."""
    image_receivers = []
    for value in values:
        if type(value) == int:
            image_receivers.append(USBCameraProcessor(value))
        elif type(value) == str:
            image_receivers.append(WebcamProcessor(value))
        else:
            raise ImageProcessorInitializingError("Values passed to create() cannot be interpreted to create cameras.")
    return image_receivers

class ImageProcessor:
    def __init__(self):
        pass

    def get_latest(self):
        raise NotImplementedError()

class RealImageProcessor(ImageProcessor):    

    def __init__(self):
        super().__init__()
        ### VIRTUAL LOCATION ###
        custom_brains = Path("/home/mulip-guest/LeRobot/lerobot/custom_brains")#import editable lerobot for VLA
        sys.path.append(custom_brains.as_posix())
        if not custom_brains.exists():
            raise ImageProcessorInitializingError(f"Could not find {custom_brains}")
        self.reader = None

    def get_latest(self):
        frame = self.reader.frame
        if not frame:
            print(f"Failed to get frame!")
        return frame

    def get_latest_data_url(self):
        frame = self.get_latest()
        return self.frame_to_data_url(frame)

    def frame_to_data_url(self, frame):
        # Encode to PNG in memory
        success, encoded = cv2.imencode(".png", frame)
        if not success:
            raise ValueError("Failed to encode frame")

        # Convert to base64 string
        b64_bytes = base64.b64encode(encoded.tobytes())
        b64_string = b64_bytes.decode("utf-8")

        # Create data URL
        return f"data:image/png;base64,{b64_string}"

class USBCameraProcessor(RealImageProcessor):
    def __init__(self, cam_idx):
        super().__init__()
        if not cam_idx:
            print(f"Webcam url missing: {cam_idx}")
            raise ImageProcessorInitializingError(f"Camera index missing: {cam_index}")
        
        try:
            from camera_readers import USBCameraReader
        except Exception as e:
            print(e)
            raise ImageProcessorInitializingError(f"Import of camera reader failed.")
        print("Starting webcam...")

        cam_cap = USBCameraReader.get_cap(cam_idx)
        self.reader = USBCameraReader(cam_cap)
    
    def start(self):
        self.reader.start()
        while self.reader.frame is None:
            print("\rWaiting... on camera")
            time.sleep(0.01)

class WebcamProcessor(RealImageProcessor):
    def __init__(self, webcam_url:str):
        super().__init__()
        if not webcam_url:
            print(f"Webcam url missing: {webcam_url}")
            raise ImageProcessorInitializingError(f"Webcam url missing: {webcam_url}")
        try:
            from camera_readers import WebcamReader
        except Exception as e:
            print(e)
            raise ImageProcessorInitializingError(f"Import of camera reader failed.")
        print("Starting webcam...")

        webcam_cap = cv2.VideoCapture(webcam_url)
        self.reader = WebcamReader(webcam_cap)
        self.reader.start()
        while self.reader.frame is None:
            print("\rWaiting... on webcam")
            time.sleep(0.01)


### Unity communication globals
HOST = "127.0.0.1"
PORT = 5000
###

class UnityImageProcessor(ImageProcessor): # And Reader
    def __init__(self):
        super().__init__()
        self.data_url = None
        self._lock = threading.Lock()

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((HOST, PORT))
        s.listen(1)
        print(f"Waiting for Unity camera connection at localhost on port {PORT}")
        self.conn, self.addr = s.accept()
        print("Connected:", self.addr)
        threading.Thread(target=self.receive_frames, daemon=True).start()

    def recv_exact(self, n):
        data = b""
        while len(data) < n:
            packet = self.conn.recv(n - len(data))
            if not packet:
                return None
            data += packet
        return data

    def receive_frames(self):
        
        print("Receiving frames in parallel thread...")
        while True:
            # Read 4-byte length
            length_bytes = self.recv_exact(4)
            if not length_bytes:
                break
            frame_len = struct.unpack("<I", length_bytes)[0]

            # Read compressed PNG frame
            frame_bytes = self.recv_exact(frame_len)
            if frame_bytes is None:
                break

            # Convert PNG → numpy → BGR for cv2
            img_array = np.frombuffer(frame_bytes, dtype=np.uint8)
            frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            self.set_latest(frame)
            cv2.imshow("Camera Stream", frame)
            if cv2.waitKey(1) == 27:  # ESC to quit
                break
        self.conn.close()
        cv2.destroyAllWindows()

    def frame_to_data_url(self, frame):
        # Encode to PNG in memory
        success, encoded = cv2.imencode(".png", frame)
        if not success:
            raise ValueError("Failed to encode frame")

        # Convert to base64 string
        b64_bytes = base64.b64encode(encoded.tobytes())
        b64_string = b64_bytes.decode("utf-8")

        # Create data URL
        return f"data:image/png;base64,{b64_string}"

    def set_latest(self, frame):
        with self._lock:
            self.data_url = self.frame_to_data_url(frame)

    def get_latest(self):
        with self._lock:
            return self.data_url