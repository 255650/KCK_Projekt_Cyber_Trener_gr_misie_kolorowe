# camera/kamera_przednia.py
import cv2
import mediapipe as mp
import numpy as np
from audio.komunikaty_glosowe import powiedz

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

POSE = mp_pose.Pose(
    static_image_mode=False,
    model_complexity=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

SHOULDER_Y_TOL = 0.04  # tolerancja dla nierównych barków
MIN_STANCE_RATIO = 1.1  # stopy 10% szerzej niż biodra
MAX_STANCE_RATIO = 1.6  # stopy maksymalnie 60% szerzej niż biodra


def process_front_frame(frame):
    if frame is None:
        return frame

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    res = POSE.process(rgb)

    if not res.pose_landmarks:
        cv2.putText(frame, "NO LANDMARKS", (30, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        return frame, [], False

    lm = res.pose_landmarks.landmark
    mp_drawing.draw_landmarks(frame, res.pose_landmarks, mp_pose.POSE_CONNECTIONS)

    l_bark = lm[11]
    p_bark = lm[12]
    p_nadgarstek = lm[15]
    p_kolano = lm[26]
    l_biodro = lm[23]
    p_biodro = lm[24]
    l_kostka = lm[27]
    p_kostka = lm[28]

    alerts = []

    if abs(l_bark.y - p_bark.y) > SHOULDER_Y_TOL:
        alerts.append("NIEROWNE BARKI")
        powiedz("Wyrównaj barki")

    szerokosc_bioder = abs(l_biodro.x - p_biodro.x)
    szerokosc_stop = abs(l_kostka.x - p_kostka.x)

    if szerokosc_bioder > 0:
        ratio = szerokosc_stop / szerokosc_bioder

        if ratio < MIN_STANCE_RATIO:
            alerts.append("STOPY ZA WASKO")
            powiedz("Ustaw stopy trochę szerzej")

        elif ratio > MAX_STANCE_RATIO:
            alerts.append("STOPY ZA SZEROKO")
            powiedz("Ustaw stopy trochę węziej")

    y = 40
    for a in alerts:
        cv2.putText(frame, a, (30, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        y += 35

    if len(alerts) == 0:
        cv2.putText(frame, "TECHNIKA OK", (30, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)



    is_down = p_nadgarstek.y > p_kolano.y + 0.02
    return frame, alerts, is_down