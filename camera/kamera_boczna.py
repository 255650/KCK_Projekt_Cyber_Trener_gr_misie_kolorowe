import numpy as np

def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
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
        alerts.append("KOLANA: Za mocno ugięte!")
    elif kat_kolan > 175:
        alerts.append("KOLANA: Ugnij kolana")

    if abs(nadgarstek[0] - kolano[0]) > 0.05:
        alerts.append("SZTANGA: Trzymaj ciężar bliżej nóg!")

    if pochylenie < 165:
        start_powtorzenia = True
    else:
        start_powtorzenia = False

    if start_powtorzenia and pochylenie < 80:
        alerts.append("UWAGA: Za duże pochylenie!")

    return alerts, start_powtorzenia


def proste_plecy(landmarks):
    nos = [landmarks[0].x, landmarks[0].y]
    bark = [landmarks[11].x, landmarks[11].y]
    biodro = [landmarks[23].x, landmarks[23].y]

    kat_plecow = calculate_angle(nos, bark, biodro)

    if kat_plecow < 165:
        return False, "Wyprostuj PLECY!"

    return True