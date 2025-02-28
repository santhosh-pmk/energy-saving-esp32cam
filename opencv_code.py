import cv2
import urllib.request
import numpy as np
import socket
import time

ESP32_URL = "http://192.168.112:81/stream" 
ESP32_IP = "192.168.112.81"
ESP32_PORT = 8888
hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

def send_status(status):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ESP32_IP, ESP32_PORT))
        sock.sendall(status.encode() + b"\n")
        sock.close()
    except Exception as e:
        print(f"Socket error: {e}")

def detect_human(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    boxes, _ = hog.detectMultiScale(gray, winStride=(8, 8))
    return len(boxes) > 0  # Returns True if humans detected

# Open stream
stream = urllib.request.urlopen(ESP32_URL)
byte_stream = b""

while True:
    byte_stream += stream.read(1024)
    a = byte_stream.find(b'\xff\xd8')
    b = byte_stream.find(b'\xff\xd9')

    if a != -1 and b != -1:
        jpg = byte_stream[a:b+2]
        byte_stream = byte_stream[b+2:]

        frame = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
        cv2.imshow("ESP32-CAM", frame)

        if detect_human(frame):
            print("Human detected!")
            send_status("present")
        else:
            print("No human detected!")
            send_status("absent")

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
