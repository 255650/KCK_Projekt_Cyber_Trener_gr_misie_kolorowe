import pyaudio as audio
import pyttsx3
from translate import Translator
import speech_recognition as sr

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

if __name__ == "__main__":
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')

    if not test_speakers():
        print("Głośniki nie działają")
    if not test_microphone():
        print("Mikrofon nie działa")

    text = ''
    text = normalize(text)
    print("Aby wybrać język powiedz polski lub angielski")
    speak("Aby wybrać język powiedz polski lub angielski")
    text = recognize("pl-PL")

    while True:
        if text == "polski":
            print("Wybrano język polski, powiedz coś (bywaj, aby zakończyć, angielski aby zmienić język): ")
            speak("Wybrano język polski, powiedz coś (bywaj, aby zakończyć, angielski aby zmienić język)")

            while text != "bywaj":
                print("...")
                text = recognize("pl-PL")
                if text == "error":
                    print("Nie rozumiem")
                    speak("Nie rozumiem")
                else:
                    text.lower().strip()
                    if text == "angielski": break
                    print("pl> " + text)
                    if is_rdl(text):
                        msg = "Wybrano rumuński martwy ciąg"
                        print(msg)
                        engine.setProperty('voice', voices[0].id)
                        speak(msg)
                        continue
                    if should_repeat(text): speak(text)
                    translator_pl_to_en = Translator(from_lang="pl", to_lang="en")
                    translated = translator_pl_to_en.translate(text).lower().strip()
                    engine.setProperty('voice', voices[1].id)
                    print("en> " + translated)
                    if should_repeat(text) or should_repeat(translated): speak(translated)
                    engine.setProperty('voice', voices[0].id)
        elif text == "angielski":
            engine.setProperty('voice', voices[1].id)
            print("English language selected, say something (goodbye to end, Polish to change language): ")
            speak("English language selected, say something (goodbye to end, Polish to change language)")

            while text != "goodbye":
                print("...")
                text = recognize("en-US")
                if text == "error":
                    print("I don't understand")
                    speak("I don't understand")
                else:
                    text.lower().strip()
                    if text == "polish":
                        engine.setProperty('voice', voices[0].id)
                        text = "polski"
                        break
                    print("en> " + text)
                    if is_rdl(text):
                        msg = "Selected Romanian deadlift"
                        print(msg)
                        engine.setProperty('voice', voices[1].id)
                        speak(msg)
                        continue
                    if should_repeat(text): speak(text)
                    translator_en_to_pl = Translator(from_lang="en", to_lang="pl")
                    translated = translator_en_to_pl.translate(text).lower().strip()
                    engine.setProperty('voice', voices[0].id)
                    print("pl> " + translated)
                    if should_repeat(text) or should_repeat(translated): speak(translated)
                    engine.setProperty('voice', voices[1].id)
        elif text == "bywaj" or text == "goodbye":
            break
        else:
            print("Nie rozumiem")
            speak("Nie rozumiem")
            text = recognize("pl-PL")
