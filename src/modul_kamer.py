import cv2
import time

class CameraError(Exception):
    pass

def try_open_camera(index):
    cap = cv2.VideoCapture(index, cv2.CAP_MSMF)

    if not cap.isOpened():
        return None

    # Wymuszenie rozdzielczości – kluczowe na Windowsie
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    # Timeout 1 sekunda na pierwszą klatkę
    start = time.time()
    while time.time() - start < 1.0:
        ret, frame = cap.read()
        if ret:
            return cap

    cap.release()
    return None


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


def start_cameras():
    try:
        cams = find_cameras()
    except CameraError:
        print("Problem z kamerą/kamerami")
        return

    while True:
        ret1, frame_front = cams[0].read()
        ret2, frame_side = cams[1].read()

        if not ret1 or not ret2:
            print("Kamera przestała zwracać klatki")
            break

        cv2.imshow('Front View', frame_front)
        cv2.imshow('Side View', frame_side)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    for cam in cams:
        cam.release()
    cv2.destroyAllWindows()
