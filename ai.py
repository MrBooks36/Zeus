from ohbot import ohbot
import ollama
import os
from time import sleep
import json
from threading import Thread
from vosk import Model, KaldiRecognizer
import pyaudio
import sys
import speech_recognition as sr
import re

CHAT_HISTORY_FILE = os.path.join(os.path.dirname(sys.modules["__main__"].__file__), "chat_history.json")
VOSK_MODEL_PATH = os.path.join(os.path.expanduser("~"), "Documents", "vosk-model")

def remove_emojis(input_string):
    emoji_pattern = re.compile(
        "[\U0001F600-\U0001F64F"
        "\U0001F300-\U0001F5FF"
        "\U0001F680-\U0001F6FF"
        "\U0001F700-\U0001F77F"
        "\U0001F780-\U0001F7FF"
        "\U0001F800-\U0001F8FF"
        "\U0001F900-\U0001F9FF"
        "\U0001FA00-\U0001FA6F"
        "\U0001FA70-\U0001FAFF"
        "\U00002700-\U000027BF"
        "\U000024C2-\U0001F251"
        "\U0001F000-\U0001F02F"
        "\U0001F0A0-\U0001F0FF"
        "]+", flags=re.UNICODE
    )
    return emoji_pattern.sub(r'', input_string)

def get_user():
    home_users = [d for d in os.listdir("/home") if os.path.isdir(os.path.join("/home", d))]
    return home_users[0] if home_users else ""

def loading():
    while not isload:
        ohbot.setEyeColour(g=10, r=0, b=0)
        sleep(0.5)
        ohbot.setEyeColour(g=0, r=10, b=0)
        sleep(0.5)
        ohbot.setEyeColour(g=0, r=0, b=10)
        sleep(0.5)
    ohbot.setEyeColour(g=0, r=0, b=0)

def load_chat_history():
    try:
        with open(CHAT_HISTORY_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_chat_history(chat_history):
    with open(CHAT_HISTORY_FILE, 'w') as file:
        json.dump(chat_history, file, indent=2)

def transcribe_with_vosk():
    model = Model(VOSK_MODEL_PATH)
    recognizer = KaldiRecognizer(model, 16000)
    audio = pyaudio.PyAudio()
    stream = audio.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
    stream.start_stream()

    try:
        print("Listening with Vosk...")
        while True:
            data = stream.read(4000, exception_on_overflow=False)
            if recognizer.AcceptWaveform(data):
                result = recognizer.Result()
                text = json.loads(result).get('text', '')
                yield text
    except GeneratorExit:
        stream.stop_stream()
    finally:
        stream.close()
        audio.terminate()

def transcribe_with_speech_recognition():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        print("Listening with SpeechRecognition...")
        while True:
            audio = recognizer.listen(source)
            try:
                text = recognizer.recognize_google(audio)
                yield text
            except sr.UnknownValueError:
                continue
            except:
                ohbot.say('Google crashed. Restart with Vosk.')
                print('Google crashed. Restart with Vosk.')
                with open('vosk', 'w') as file:
                    file.close()

                return

def ai(USE_SPEECH_RECOGNITION):
    global isload
    isload = 0
    chat_history = load_chat_history()

    transcription_generator = (
        transcribe_with_speech_recognition() if USE_SPEECH_RECOGNITION else transcribe_with_vosk()
    )

    with open(os.path.join(os.path.dirname(__file__), 'ai.txt'), 'r') as file:
        role = file.read()

    ollama.create(model='Zeus', from_='gemma3:1b', system=role)

    try:
        for text in transcription_generator:
            print(f"You said: {text}")

            if text.lower() == 'exit':
                save_chat_history(chat_history)
                exit(0)


            if text:
                chat_history.append({'role': 'user', 'content': text})
                thr = Thread(target=loading)
                thr.start()

                response = ollama.chat(model='Zeus', messages=chat_history, options={'temperature': 0.7})
                isload = 1
                thr.join()

                say = str(response['message']['content'])
                say = remove_emojis(say.replace('*', ''))
                print(say)

                chat_history.append({'role': 'assistant', 'content': say})
                save_chat_history(chat_history)

                ohbot.say(say)

    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    ai(USE_SPEECH_RECOGNITION=True)  # or True if using Google SR