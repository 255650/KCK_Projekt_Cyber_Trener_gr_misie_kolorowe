import pyaudio as audio
import pyttsx3
from translate import Translator
from audio.komunikaty_glosowe import powiedz
import speech_recognition as sr

engine = None

def test_microphone():
    au = audio.PyAudio()
    try:
        stream = au.open(format=audio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)
        stream.close()
        return True
    except:
        return False

def microphone_aval():
    au = audio.PyAudio()
    for i in range(au.get_device_count()):
        device_info = au.get_device_info_by_index(i)
        if device_info["maxInputChannels"] > 0:
            if test_microphone():
                au.terminate()
                return True
    au.terminate()
    return False

def test_speakers():
    au = audio.PyAudio()
    try:
        stream = au.open(format=audio.paInt16, channels=1, rate=44100, output=True, frames_per_buffer=1024)
        stream.close()
        return True
    except:
        return False

def speakers():
    au = audio.PyAudio()
    for i in range(au.get_device_count()):
        device = au.get_device_info_by_index(i)
        if device["maxOutputChannels"] > 0:
            if test_speakers():
                au.terminate()
                return True
    au.terminate()
    return False


def recognize(language):
    rec = sr.Recognizer()
    rec.energy_threshold = 300
    rec.dynamic_energy_threshold = True
    rec.pause_threshold = 0.8

    try:
        with sr.Microphone() as source:
            rec.adjust_for_ambient_noise(source, duration=0.7)
            audio_data = rec.listen(source,timeout=6,phrase_time_limit=6)

            text =  rec.recognize_google(audio_data, language=language)
            return text.lower().strip()
    except sr.WaitTimeoutError:
        return "timeout"
    except sr.UnknownValueError:
        return "unknown"
    except Exception:
        return "error"

def speak(text):
    engine.say(text)
    engine.startLoop(False)
    while engine.isBusy():
        engine.iterate()
    engine.endLoop()

KEYWORDS_REPEAT = {"rumuński martwy ciąg", "romanian deadlift", "bywaj", "goodbye"}
RDL_KEYWORDS_PL = {"rumuński martwy ciąg", "romanian deadlift"}
RDL_KEYWORDS_EN = {"romanian deadlift", "rumuński martwy ciąg"}

def should_repeat(text):
    return text in KEYWORDS_REPEAT

def is_rdl(text):
    return text in RDL_KEYWORDS_PL or text in RDL_KEYWORDS_EN

def normalize(text):
    return text.replace(" ", "").lower().strip()

def run_translator():
    global engine

    engine = pyttsx3.init()
    voices = engine.getProperty('voices')

    if not test_speakers():
        print("Głośniki nie działają")
    if not test_microphone():
        print("Mikrofon nie działa")

    text = ''
    text = normalize(text)

    print("Aby wybrać język powiedz polski lub angielski")
    powiedz("Aby wybrać język powiedz polski lub angielski")
    text = recognize("pl-PL")

    while True:
        if text == "polski":
            print("Wybrano język polski, powiedz nazwę ćwiczenia")
            powiedz("Wybrano język polski, powiedz nazwę ćwiczenia")

            while text != "bywaj":
                print("...")
                text = recognize("pl-PL")

                if text in ["error", "unknown", "timeout"]:
                    print("Nie rozumiem")
                    powiedz("Nie rozumiem")
                    continue

                if text == "angielski":
                    break

                print("pl> " + text)

                if is_rdl(text):
                    msg = "Wybrano rumuński martwy ciąg"
                    print(msg)
                    engine.setProperty('voice', voices[0].id)
                    powiedz(msg)
                    continue

        elif text == "angielski":
            engine.setProperty('voice', voices[1].id)

            print("English language selected, say exercise name")
            powiedz("English language selected, say exercise name")

            while text != "goodbye":
                print("...")
                text = recognize("en-US")

                if text in ["error", "unknown", "timeout"]:
                    print("I don't understand")
                    powiedz("I don't understand")
                    continue

                if text == "polish":
                    engine.setProperty('voice', voices[0].id)
                    text = "polski"
                    break

                print("en> " + text)

                if is_rdl(text):
                    msg = "Selected Romanian deadlift"
                    print(msg)
                    engine.setProperty('voice', voices[1].id)
                    powiedz(msg)
                    continue

        elif text == "bywaj" or text == "goodbye":
            break

        else:
            print("Nie rozumiem")
            powiedz("Nie rozumiem")
            text = recognize("pl-PL")

if __name__ == "__main__":
    run_translator()