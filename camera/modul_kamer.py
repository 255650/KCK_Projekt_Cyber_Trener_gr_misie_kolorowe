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

        if len(available) == 2:
            return available

    for cap in available:
        cap.release()

    raise CameraError("Nie znaleziono dwóch działających kamer.")

#Uruchamia okna z dwóch znalezionych kamery
def start_cameras():
    cams = find_cameras()

    while True:
        ret1, frame_front = cams[0].read()
        ret2, frame_side = cams[1].read()

        if not ret1 or not ret2:
            raise CameraError("Kamera przestała zwracać klatki.")

        cv2.imshow('Front View', frame_front)
        cv2.imshow('Side View', frame_side)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    for cam in cams:
        cam.release()
    cv2.destroyAllWindows()
