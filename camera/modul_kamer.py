import cv2
import subprocess

class CameraError(Exception):
    pass

def video_divaces_count():
    result = subprocess.run(["wmic", "path", "Win32_PnPEntity", "where", "Service='usbvideo'", "get", "Name"],
    capture_output = True, text=True)

    lines = result.stdout.splitlines()[1:]
    count = 0
    for line in lines:
        line = line.strip()
        if line:
            count+=1
    return count

def find_cameras():
    devices_number = video_divaces_count()
    available = []

    for i in range(devices_number):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                available.append(cap)
            else:
                cap.release()
        else:
            cap.release()

        if len(available) == 2:
            return available

    for cap in available:
        cap.release()
    raise CameraError


def start_cameras():
    try:
        cams = find_cameras()
    except CameraError:
        print("Problem z kamerą/kamerami")
        return

    while True:
        ret1, frame_front = cams[0].read()
        ret2, frame_side = cams[1].read()

        cv2.imshow('Front View',frame_front)
        cv2.imshow('Side View',frame_side)

        if cv2.getWindowProperty('Front View',cv2.WND_PROP_VISIBLE) < 1:
            break
        if cv2.getWindowProperty('Side View',cv2.WND_PROP_VISIBLE) < 1:
            break

    cams[0].release()
    cams[1].release()
    cv2.destroyAllWindows()