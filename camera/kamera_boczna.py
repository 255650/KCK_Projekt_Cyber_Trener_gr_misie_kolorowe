import cv2
import mediapipe as mp
import numpy as np


mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

pose_side = mp_pose.Pose(
    static_image_mode=False,
    model_complexity=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

angle_buffer = {
    "knee": None,
    "hip": None,
    "back": None
}

def smooth_angle(name, value, alpha=0.75):
    if angle_buffer[name] is None:
        angle_buffer[name] = value
    else:
        angle_buffer[name] = alpha * angle_buffer[name] + (1 - alpha) * value
    return angle_buffer[name]


def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(
        a[1] - b[1],
        a[0] - b[0]
    )

    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180.0:
        angle = 360 - angle

    return angle


last_phase = "GÓRA"

def get_phase(hip_angle):
    global last_phase

    if hip_angle > 158:
        last_phase = "GÓRA"
    elif hip_angle < 142:
        last_phase = "DÓŁ"

    return last_phase


def knee_zone(angle):
    if 150 <= angle <= 170:
        return "OK"
    elif 140 <= angle < 150:
        return "ZBYT MOCNE UGIĘCIE KOLAN"
    elif 170 < angle <= 180:
        return "KOLANA ZBYT PROSTE"
    else:
        return "POZA ZAKRESEM RUCHU"


def analyze_rdl(landmarks):
    if not landmarks:
        return [], False

    alerts = []

    bark = [landmarks[11].x, landmarks[11].y]
    biodro = [landmarks[23].x, landmarks[23].y]
    kolano = [landmarks[25].x, landmarks[25].y]
    kostka = [landmarks[27].x, landmarks[27].y]
    nadgarstek = [landmarks[15].x, landmarks[15].y]

    knee_angle_raw = calculate_angle(biodro, kolano, kostka)
    hip_angle_raw = calculate_angle(bark, biodro, kolano)

    knee_angle = smooth_angle("knee", knee_angle_raw)
    hip_angle = smooth_angle("hip", hip_angle_raw)

    phase = get_phase(hip_angle)

    knee_state = knee_zone(knee_angle)
    if knee_state != "OK":
        alerts.append(f"KOLANA: {knee_state}")

    if abs(nadgarstek[0] - kolano[0]) > 0.12:
        alerts.append("CIĘŻAR: TRZYMAJ BLIŻEJ NÓG")

    if phase == "DOWN" and hip_angle < 120:
        alerts.append("BIODRA: ZBYT NISKO, KONTROLUJ RUCH")

    start_powtorzenia = (phase == "DOWN")

    return alerts, start_powtorzenia


def proste_plecy(landmarks):
    nos = [landmarks[0].x, landmarks[0].y]
    bark = [landmarks[11].x, landmarks[11].y]
    biodro = [landmarks[23].x, landmarks[23].y]

    kat_plecow = calculate_angle(nos, bark, biodro)
    kat_plecow = smooth_angle("back", kat_plecow)

    if kat_plecow < 165:
        return False, "PLECY: UTRZYMAJ NEUTRALNĄ POZYCJĘ"

    return True, ""


def process_side_frame(frame):
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = pose_side.process(rgb)

    if not result.pose_landmarks:
        return frame

    landmarks = result.pose_landmarks.landmark

    mp_drawing.draw_landmarks(
        frame,
        result.pose_landmarks,
        mp_pose.POSE_CONNECTIONS
    )

    alerts, start_rep = analyze_rdl(landmarks)
    back_ok, back_alert = proste_plecy(landmarks)

    if not back_ok:
        alerts.append(back_alert)

    y = 40

    for alert in alerts:
        cv2.putText(
            frame,
            alert,
            (30, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 0, 255),
            2
        )
        y += 35

    if len(alerts) == 0:
        cv2.putText(
            frame,
            "OK: DOBRA TECHNIKA",
            (30, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )

    if start_rep:
        cv2.putText(
            frame,
            "FAZA: RUCH W DÓŁ",
            (30, y + 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 0),
            2
        )

    return frame