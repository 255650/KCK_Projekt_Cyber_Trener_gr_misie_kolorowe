# camera/kamera_przednia.py
import cv2
import mediapipe as mp
import numpy as np
from camera.analiza import update_front

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
POSE_FRONT = mp_pose.Pose(static_image_mode=False, model_complexity=1,
                          min_detection_confidence=0.5, min_tracking_confidence=0.5)

SYMMETRY_TOL = 0.04
FOOT_HIP_RATIO_MIN = 0.8
FOOT_HIP_RATIO_MAX = 1.8

def calculate_angle(a, b, c):
    a = np.array(a); b = np.array(b); c = np.array(c)
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = abs(radians * 180.0 / np.pi)
    if angle > 180.0:
        angle = 360 - angle
    return angle

def process_front_frame(frame):
    """
    Kompatybilne API: przyjmuje BGR frame, rysuje overlay i zwraca frame.
    Dodatkowo wywołuje update_front(score, max_score).
    Zmiana: score = max_score - liczba_alertów (każdy alert obniża technikę).
    """
    if frame is None:
        update_front(0, 2)
        return frame

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    res = POSE_FRONT.process(rgb)
    if not res.pose_landmarks:
        update_front(0, 2)
        return frame

    landmarks = res.pose_landmarks.landmark
    mp_drawing.draw_landmarks(frame, res.pose_landmarks, mp_pose.POSE_CONNECTIONS)

    alerts = []
    max_score = 2

    try:
        lb = [landmarks[11].x, landmarks[11].y]
        rb = [landmarks[12].x, landmarks[12].y]
        lh = [landmarks[23].x, landmarks[23].y]
        rh = [landmarks[24].x, landmarks[24].y]
        la = [landmarks[27].x, landmarks[27].y]
        ra = [landmarks[28].x, landmarks[28].y]
    except Exception:
        update_front(0, max_score)
        return frame

    # symetria barków
    if abs(lb[1] - rb[1]) > SYMMETRY_TOL:
        alerts.append("SYMETRIA BARKOW")

    # rozstaw stóp vs bioder
    hip_width = abs(lh[0] - rh[0])
    foot_width = abs(la[0] - ra[0])
    if not (hip_width > 0 and FOOT_HIP_RATIO_MIN <= (foot_width / hip_width) <= FOOT_HIP_RATIO_MAX):
        alerts.append("ROZSTAW STOP")

    # score = max_score - liczba alertów (więcej alertów -> mniejszy score)
    score = max(0, max_score - len(alerts))

    # overlay frontowe
    y = 10
    for a in alerts:
        cv2.putText(frame, a, (10, y+20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255), 2)
        y += 25
    if not alerts:
        cv2.putText(frame, "FRONT: OK", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)

    # zaktualizuj centralną analizę (snapshot front)
    update_front(score, max_score)
    return frame
