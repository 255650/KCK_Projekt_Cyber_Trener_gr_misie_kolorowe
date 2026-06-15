state = "up"
reps = 0
total_frames = 0
good_frames = 0

def update_reps(is_down, is_up, front_alerts, side_alerts):
    global state, reps, total_frames, good_frames

    # zliczanie poprawnych i błędnych klatek
    total_frames += 1
    if len(front_alerts) == 0 and len(side_alerts) == 0:
        good_frames += 1

    # procent techniki
    if total_frames > 0:
        technique_percent = (good_frames / total_frames) * 100
    else:
        technique_percent = 100

    # powtórzenie
    if state == "up":
        if is_down:
            state = "down"
            total_frames = 0
            good_frames = 0

    elif state == "down":
        if is_up:
            state = "up"
            if technique_percent >= 80:
                reps += 1

    return reps, int(technique_percent)

def reset_session():
    global state, reps, total_frames, good_frames
    state = "up"
    reps = 0
    total_frames = 0
    good_frames = 0
