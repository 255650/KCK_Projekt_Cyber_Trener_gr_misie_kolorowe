import time
import threading
import win32com.client

last_times = {}
cooldown = 5
speaking = False


def _speak(text):
    global speaking

    try:
        speaking = True
        speaker = win32com.client.Dispatch("SAPI.SpVoice")
        speaker.Rate = 0
        speaker.Volume = 100

        print("Mowie:", text)
        speaker.Speak(text)

    except Exception as e:
        print("Blad mowy:", e)

    finally:
        speaking = False


def powiedz(text):
    global speaking

    now = time.time()

    if text in last_times and now - last_times[text] < cooldown:
        return

    if speaking:
        return

    last_times[text] = now

    thread = threading.Thread(target=_speak, args=(text,), daemon=True)
    thread.start()


def uruchom_glos():
    pass