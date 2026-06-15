# camera/kamera_boczna.py
import cv2
import mediapipe as mp
import numpy as np

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

POSE = mp_pose.Pose(
    static_image_mode=False,
    model_complexity=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# PROGI
ELBOW_BELOW_KNEE_TOL = 0.05     # tolerancja - łokieć nie może być niżej niż kolano
ELBOW_X_TOL = 0.05              # łokieć nie może być za daleko od nogi (w osi X)

def knee_angle(a, b, c):
    a = np.array(a); b = np.array(b); c = np.array(c)
    ang = np.degrees(np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0]))
    ang = abs(ang)
    if ang > 180:
        ang = 360 - ang
    return ang

def process_side_frame(frame):
    if frame is None:
        return frame

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    res = POSE.process(rgb)

    if not res.pose_landmarks:
        cv2.putText(frame, "NO LANDMARKS", (30, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255), 2)
        return frame

    lm = res.pose_landmarks.landmark
    mp_drawing.draw_landmarks(frame, res.pose_landmarks, mp_pose.POSE_CONNECTIONS)

    # Pobranie punktów
    bark = lm[11]
    biodro = lm[23]
    kolano = lm[25]
    kostka = lm[27]
    lokiec = lm[13]

    alerts = []

    #ŁOKIEĆ nie może być niżej niż kolano
    if lokiec.y > kolano.y + ELBOW_BELOW_KNEE_TOL:
        alerts.append("SZTANGA ZA NISKO")

    #BARK nie może być niżej niż biodro
    if bark.y > biodro.y:
        alerts.append("ZA NISKO")

    #KOLANO odpowiedni kąt
    k_angle = knee_angle(
        (biodro.x, biodro.y),
        (kolano.x, kolano.y),
        (kostka.x, kostka.y)
    )
    if not (150 <= k_angle <= 175):
        alerts.append("KOLANO")

    # Rysowanie alertów
    y = 40
    for a in alerts:
        cv2.putText(frame, a, (30, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255), 2)
        y += 35

    if len(alerts) == 0:
        cv2.putText(frame, "TECHNIKA OK", (30, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)

    return frame
