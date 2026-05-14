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


def analyze_rdl(landmarks):
    alerts = []

    bark = [landmarks[11].x, landmarks[11].y]
    biodro = [landmarks[23].x, landmarks[23].y]
    kolano = [landmarks[25].x, landmarks[25].y]
    kostka = [landmarks[27].x, landmarks[27].y]
    nadgarstek = [landmarks[15].x, landmarks[15].y]

    kat_kolan = calculate_angle(biodro, kolano, kostka)
    pochylenie = calculate_angle(bark, biodro, kolano)

    if kat_kolan < 145:
        alerts.append("KOLANA: Za mocno ugiete!")
    elif kat_kolan > 175:
        alerts.append("KOLANA: Ugnij kolana")

    if abs(nadgarstek[0] - kolano[0]) > 0.05:
        alerts.append("SZTANGA: Trzymaj ciezar blizej nog!")

    if pochylenie < 165:
        start_powtorzenia = True
    else:
        start_powtorzenia = False

    if start_powtorzenia and pochylenie < 80:
        alerts.append("UWAGA: Za duze pochylenie!")

    return alerts, start_powtorzenia


def proste_plecy(landmarks):
    nos = [landmarks[0].x, landmarks[0].y]
    bark = [landmarks[11].x, landmarks[11].y]
    biodro = [landmarks[23].x, landmarks[23].y]

    kat_plecow = calculate_angle(nos, bark, biodro)

    if kat_plecow < 165:
        return False, "Wyprostuj PLECY!"

    return True, ""


def process_side_frame(frame):
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    result = pose_side.process(rgb)

    if result.pose_landmarks:
        landmarks = result.pose_landmarks.landmark

        mp_drawing.draw_landmarks(
            frame,
            result.pose_landmarks,
            mp_pose.POSE_CONNECTIONS
        )

        alerts, start_powtorzenia = analyze_rdl(landmarks)
        plecy_ok, plecy_alert = proste_plecy(landmarks)

        if not plecy_ok:
            alerts.append(plecy_alert)

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
                "TECHNIKA POPRAWNA",
                (30, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2
            )

        if start_powtorzenia:
            cv2.putText(
                frame,
                "RUCH W DOL",
                (30, y + 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 0),
                2
            )

    return frame