import socket
import threading
import time
import math

import kinematics

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 5007

class ThroughMessage(threading.Thread):
    def __init__(self, shared):
        super().__init__()
        self.lock = threading.Lock()
        self.shared = shared

    def run(self):
        while True:
            try:
                while True:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.connect((HOST, PORT))
                        with self.lock:
                            message = self.shared["target_message"]
                            s.sendall(message.encode('utf-8'))
            except ConnectionRefusedError:
                print(f"Socket {HOST}:{PORT} is down.")
                time.sleep(2)

class ThroughJoints(threading.Thread):
    def __init__(self, shared):
        super().__init__()
        self.lock = threading.Lock()
        self.shared = shared

    def run(self):
        while True:
            try:
                while True:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.connect((HOST, PORT))
                        with self.lock:
                            joints = str(self.shared["target_joints"])
                            #print("Sending", joints)
                            s.sendall(bytes(joints, 'utf-8'))
                        data = s.recv(1024)


                        self.shared["present_joints"] = [math.radians(float(angle)) for angle in str(data).split(",")[1:7]]
                        print(self.shared)
                    #print(f"Received {data!r}")
            except KeyboardInterrupt:
                joints = input("Joints:\n") + "\n" 
            except ConnectionRefusedError:
                print(f"Socket {HOST}:{PORT} is down.")



def main():
    shared = {"target_joints": [0.0, 0.0,0.0,0.0,0.0,0.0,0.0,0.0], "present_joints":None}
    through_thread = ThroughJoints(shared)
    through_thread.start()
    
    while True:
        #
        if shared["present_joints"]:
            print(shared)
            break
    present_joints = shared["present_joints"]
    
    k = kinematics.Kinematics()
    result = k.forward(present_joints)
    
    while True:
        #result = k.forward(present_joints)
        q = k.inverse()
        shared["target_joints"] = list(q[-7:])
        pass


if __name__ == "__main__":
    main()
