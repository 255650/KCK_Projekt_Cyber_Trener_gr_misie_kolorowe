import cv2
import time

class CameraError(Exception):
    pass

#Testuje pojedyńczą kamerę
def try_open_camera(index):
    try:
        cap = cv2.VideoCapture(index, cv2.CAP_MSMF)
    except Exception:
        return None
    if not cap.isOpened():
        return None
    start = time.time()
    while time.time() - start < 1.0:
        ret, frame = cap.read()
        if ret:
            return cap
    cap.release()
    return None

#Szuka dostępnych kamer
def find_cameras(max_tested=10):
    available = []
    for i in range(max_tested):
        cap = try_open_camera(i)
        if cap:
            available.append(cap)
    if len(available) == 0:
        raise CameraError("Nie znaleziono żadnej kamery.")
    return available