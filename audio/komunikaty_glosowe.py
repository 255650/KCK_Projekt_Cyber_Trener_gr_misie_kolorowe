import time
import threading
import win32com.client


last_times = {}
cooldown = 5

speaking = False
speaking_lock = threading.Lock()


def _speak(text):
    global speaking

    with speaking_lock:
        try:
            speaking = True

            speaker = win32com.client.Dispatch("SAPI.SpVoice")
            speaker.Rate = 0
            speaker.Volume = 100
            speaker.Speak(text)

        except Exception as error:
            print("Błąd mowy:", error)

        finally:
            speaking = False


def powiedz(text):
    global speaking

    now = time.time()

    # Nie powtarza tego samego komunikatu przez 5 sekund
    if text in last_times and now - last_times[text] < cooldown:
        return

    # Nie rozpoczyna nowego komunikatu podczas mówienia
    if speaking:
        return

    last_times[text] = now

    thread = threading.Thread(
        target=_speak,
        args=(text,),
        daemon=True
    )

    thread.start()