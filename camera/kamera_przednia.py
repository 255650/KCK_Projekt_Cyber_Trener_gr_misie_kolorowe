import cv2
import mediapipe as mp


mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

pose_front = mp_pose.Pose(
    static_image_mode=False,
    model_complexity=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)


def analizuj_przod(punkty):
    alerty = []

    lewy_bark = [punkty[11].x, punkty[11].y]
    prawy_bark = [punkty[12].x, punkty[12].y]

    lewe_biodro = [punkty[23].x, punkty[23].y]
    prawe_biodro = [punkty[24].x, punkty[24].y]

    lewe_kolano = [punkty[25].x, punkty[25].y]
    prawe_kolano = [punkty[26].x, punkty[26].y]

    lewa_kostka = [punkty[27].x, punkty[27].y]
    prawa_kostka = [punkty[28].x, punkty[28].y]

    szerokosc_bioder = abs(lewe_biodro[0] - prawe_biodro[0])
    szerokosc_stop = abs(lewa_kostka[0] - prawa_kostka[0])

    if szerokosc_bioder == 0:
        return alerty

    stosunek_rozkroku = szerokosc_stop / szerokosc_bioder

    if stosunek_rozkroku < 1.0:
        alerty.append("ROZKROK: Za wasko!")
    elif stosunek_rozkroku > 1.5:
        alerty.append("ROZKROK: Za szeroko!")

    roznica_barkow = abs(lewy_bark[1] - prawy_bark[1])

    if roznica_barkow > 0.03:
        alerty.append("SYMETRIA: Barki nierowno!")

    if lewe_kolano[0] > lewa_kostka[0]:
        alerty.append("KOLANA: Lewe kolano ucieka do srodka!")

    if prawe_kolano[0] < prawa_kostka[0]:
        alerty.append("KOLANA: Prawe kolano ucieka do srodka!")

    return alerty


def process_front_frame(frame):
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    result = pose_front.process(rgb)

    if result.pose_landmarks:
        punkty = result.pose_landmarks.landmark

        mp_drawing.draw_landmarks(
            frame,
            result.pose_landmarks,
            mp_pose.POSE_CONNECTIONS
        )

        alerty = analizuj_przod(punkty)

        y = 40

        for alert in alerty:
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

        if len(alerty) == 0:
            cv2.putText(
                frame,
                "TECHNIKA POPRAWNA",
                (30, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2
            )

    return frame