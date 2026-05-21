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


# Zunifikowane nazwy faz na "DOWN" i "UP", żeby pasowały do logiki warunkowej
last_phase = "UP"

def get_phase(hip_angle):
    global last_phase

    if hip_angle > 158:
        last_phase = "UP"
    elif hip_angle < 142:
        last_phase = "DOWN"

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


# KROK 1: Przekazujemy słownik z indeksami wybranego boku ciała
def analyze_rdl(landmarks, p_idx):
    if not landmarks:
        return [], False, "UP"

    alerts = []

    # Mapowanie punktów na podstawie przesłanych indeksów bezpiecznego boku
    bark = [landmarks[p_idx["bark"]].x, landmarks[p_idx["bark"]].y]
    biodro = [landmarks[p_idx["biodro"]].x, landmarks[p_idx["biodro"]].y]
    kolano = [landmarks[p_idx["kolano"]].x, landmarks[p_idx["kolano"]].y]
    kostka = [landmarks[p_idx["kostka"]].x, landmarks[p_idx["kostka"]].y]
    nadgarstek = [landmarks[p_idx["nadgarstek"]].x, landmarks[p_idx["nadgarstek"]].y]

    knee_angle_raw = calculate_angle(biodro, kolano, kostka)
    hip_angle_raw = calculate_angle(bark, biodro, kolano)

    knee_angle = smooth_angle("knee", knee_angle_raw)
    hip_angle = smooth_angle("hip", hip_angle_raw)

    phase = get_phase(hip_angle)

    # Kolana sprawdzamy głównie w górze i w trakcie zejścia,
    # ale z większą tolerancją w dolnej fazie
    if phase == "UP":
        if knee_angle < 145:
            alerts.append("KOLANA: ZA MOCNO UGIETE")
    elif phase == "DOWN":
        if knee_angle < 135:
            alerts.append("KOLANA: ZA MOCNO UGIETE")

    # Ciężar też ma większą tolerancję, bo z boku punkty mogą pływać
    if abs(nadgarstek[0] - kolano[0]) > 0.18:
        alerts.append("CIEZAR: TRZYMAJ BLIZEJ NOG")

    # Biodra — nie blokujemy normalnego zejścia w RDL
    if phase == "DOWN" and hip_angle < 95:
        alerts.append("BIODRA: ZA NISKO")

    start_powtorzenia = (phase == "DOWN")

    return alerts, start_powtorzenia, phase


# KROK 2: Funkcja pleców również przyjmuje dynamiczne indeksy boku
def proste_plecy(landmarks, p_idx):
    bark = [landmarks[p_idx["bark"]].x, landmarks[p_idx["bark"]].y]
    biodro = [landmarks[p_idx["biodro"]].x, landmarks[p_idx["biodro"]].y]
    kolano = [landmarks[p_idx["kolano"]].x, landmarks[p_idx["kolano"]].y]

    # Kąt tułowia względem uda
    kat_tulowia = calculate_angle(bark, biodro, kolano)
    kat_tulowia = smooth_angle("back", kat_tulowia)

    # Większa tolerancja, żeby nie krzyczało cały czas
    if kat_tulowia < 95:
        return False, "PLECY: NIE ZAOKRAGLAJ PLECOW"

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

    # KROK 3: WYKORZYSTANIE 3 WYMIARU (OŚ Z)
    # Sprawdzamy głębokość lewego (23) i prawego (24) biodra.
    # Mniejsza (bardziej ujemna) wartość oznacza punkt bliżej obiektywu kamery.
    if landmarks[23].z < landmarks[24].z:
        # Lewy bok jest bliżej kamery - bierzemy lewe indeksy
        p_idx = {"bark": 11, "biodro": 23, "kolano": 25, "kostka": 27, "nadgarstek": 15}
    else:
        # Prawy bok jest bliżej kamery - bierzemy prawe indeksy
        p_idx = {"bark": 12, "biodro": 24, "kolano": 26, "kostka": 28, "nadgarstek": 16}

    # Przekazujemy odfiltrowane indeksy boku do funkcji analitycznych
    alerts, start_rep, phase = analyze_rdl(landmarks, p_idx)
    back_ok, back_alert = proste_plecy(landmarks, p_idx)

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
            "FAZA: RUCH W DOL",
            (30, y + 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 0),
            2
        )
    elif phase == "UP":
        cv2.putText(
            frame,
            "FAZA: RUCH W GORE",
            (30, y + 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 0),
            2
        )

    return frame