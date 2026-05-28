# camera/kamera_boczna.py
import cv2
import mediapipe as mp
import numpy as np
from camera.analiza import update_side, get_rep_count

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
POSE_SIDE = mp_pose.Pose(static_image_mode=False, model_complexity=1,
                        min_detection_confidence=0.5, min_tracking_confidence=0.5)

ALPHA = 0.75
KNEE_OK_MIN, KNEE_OK_MAX = 140, 180
HORIZONTAL_THRESHOLD = 0.22
BACK_OK_THRESHOLD = 75            # surowszy próg dla pleców
HIP_LOW_THRESHOLD = 95            # surowszy próg bioder
HAND_BELOW_FRAMES_THRESHOLD = 2

angle_buffer = {"knee": None, "hip": None, "back": None}
hand_below_counter = 0

def smooth_angle(name, value, alpha=ALPHA):
    if angle_buffer[name] is None:
        angle_buffer[name] = value
    else:
        angle_buffer[name] = alpha * angle_buffer[name] + (1 - alpha) * value
    return angle_buffer[name]

def calculate_angle(a, b, c):
    a = np.array(a); b = np.array(b); c = np.array(c)
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = abs(radians * 180.0 / np.pi)
    if angle > 180.0:
        angle = 360 - angle
    return angle

def process_side_frame(frame):
    """
    Kompatybilne API: przyjmuje BGR frame, rysuje overlay i zwraca frame.
    Zmiany:
      - score = max_score - liczba_alertów (błędy silniej obniżają technikę)
      - surowsze progi dla pleców i bioder
      - snapshot ostatniej klatki zapisywany w analysis przez update_side
    """
    global hand_below_counter

    if frame is None:
        update_side(0, 3, {})
        return frame

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    res = POSE_SIDE.process(rgb)
    if not res.pose_landmarks:
        hand_below_counter = 0
        update_side(0, 3, {})
        return frame

    landmarks = res.pose_landmarks.landmark
    mp_drawing.draw_landmarks(frame, res.pose_landmarks, mp_pose.POSE_CONNECTIONS)

    p = {"bark":11, "biodro":23, "kolano":25, "kostka":27, "nadgarstek":15}
    try:
        bark = [landmarks[p["bark"]].x, landmarks[p["bark"]].y]
        biodro = [landmarks[p["biodro"]].x, landmarks[p["biodro"]].y]
        kolano = [landmarks[p["kolano"]].x, landmarks[p["kolano"]].y]
        kostka = [landmarks[p["kostka"]].x, landmarks[p["kostka"]].y]
        nadgarstek = [landmarks[p["nadgarstek"]].x, landmarks[p["nadgarstek"]].y]
    except Exception:
        update_side(0, 3, {})
        return frame

    knee_raw = calculate_angle(biodro, kolano, kostka)
    hip_raw = calculate_angle(bark, biodro, kolano)
    back_raw = calculate_angle(bark, biodro, kolano)

    knee = smooth_angle("knee", knee_raw)
    hip = smooth_angle("hip", hip_raw)
    back = smooth_angle("back", back_raw)

    # phase
    phase = "UP"
    if hip < 142:
        phase = "DOWN"
    elif hip > 158:
        phase = "UP"

    alerts = []
    max_score = 3

    # kolana
    if not (KNEE_OK_MIN <= knee <= KNEE_OK_MAX):
        alerts.append("KOLANA")

    # ciężar (nadgarstek względem kolana)
    if not (abs(nadgarstek[0] - kolano[0]) <= HORIZONTAL_THRESHOLD):
        alerts.append("CIEZAR")

    # biodra (surowszy próg)
    if phase == "DOWN" and hip < HIP_LOW_THRESHOLD:
        alerts.append("BIODRA ZA NISKO")

    # plecy (surowszy próg)
    if back < BACK_OK_THRESHOLD:
        alerts.append("PLECY")

    # hands below detection
    hands_below = False
    if nadgarstek[1] > kolano[1]:
        hand_below_counter += 1
    else:
        hand_below_counter = 0
    if hand_below_counter >= HAND_BELOW_FRAMES_THRESHOLD:
        hands_below = True

    # jeśli ręce poniżej i blisko ciała, złagodź niektóre alerty (kontekst RDL)
    if hands_below and abs(nadgarstek[0] - kolano[0]) <= HORIZONTAL_THRESHOLD:
        alerts = [a for a in alerts if a not in ("BIODRA ZA NISKO",)]
        # nie usuwamy alertu PLECY — plecy są teraz surowiej oceniane i nie są ignorowane
        # dajemy małą premię tylko jeśli nie ma innych alertów
        if len(alerts) == 0:
            # jeśli nie ma żadnych alertów, dajemy pełny score
            pass

    # score = max_score - liczba alertów (błędy silniej obniżają technikę)
    score = max(0, max_score - len(alerts))

    extra = {"phase": phase, "start_rep": phase == "DOWN", "knee_angle": knee, "hip_angle": hip, "hands_below": hands_below}
    update_side(score, max_score, extra)

    # overlay alertów
    y = 40
    for a in alerts:
        cv2.putText(frame, a, (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255), 2); y += 30
    if not alerts:
        cv2.putText(frame, "SIDE: OK", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

    # pokaż liczbę powtórzeń
    try:
        rep_count = get_rep_count()
    except Exception:
        rep_count = 0
    cv2.putText(frame, f"POWTORZENIA: {rep_count}", (10, frame.shape[0]-30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255,255,255), 2)

    # debug po prawej
    dbg_x = frame.shape[1] - 260; dbg_y = 30
    cv2.putText(frame, f"phase:{phase}", (dbg_x, dbg_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200,200,0), 2)
    cv2.putText(frame, f"knee:{int(knee)}", (dbg_x, dbg_y+25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200,200,0), 2)
    cv2.putText(frame, f"hip:{int(hip)}", (dbg_x, dbg_y+50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200,200,0), 2)
    cv2.putText(frame, f"back:{int(back)}", (dbg_x, dbg_y+75), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200,200,0), 2)
    cv2.putText(frame, f"hands_below:{int(hand_below_counter)}", (dbg_x, dbg_y+100), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200,200,0), 2)

    return frame
