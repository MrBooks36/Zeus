from ohbotfix import ohbot
import ollama
import os
from time import sleep
import json
from threading import Thread
from vosk import Model, KaldiRecognizer
import pyaudio
from platform import system

CHAT_HISTORY_FILE = os.path.join(os.path.expanduser("~"), "chat_history.json")

VOSK_MODEL_PATH = os.path.join(os.path.expanduser("~"), "Documents", "vosk-model")

print(VOSK_MODEL_PATH)

def get_user():
    home_users = [d for d in os.listdir("/home") if os.path.isdir(os.path.join("/home", d))]
    return home_users[0] if home_users else ""  # fallback default

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

def ai():
    global isload
    isload = 0
    chat_history = load_chat_history()

    # Initialize the Vosk model
    model = Model(VOSK_MODEL_PATH)
    recognizer = KaldiRecognizer(model, 16000)

    with open(os.path.join(os.path.dirname(__file__), 'ai.txt'), 'r') as file:
        role = file.read()

    ollama.create(model='Zeus', from_='gemma3:1b',system=role)
    
    sleep(4)
    audio = pyaudio.PyAudio()

    # Open a new stream for audio input
    stream = audio.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
    stream.start_stream()

    print("Listening...")

    try:
        while True:
            data = stream.read(4000, exception_on_overflow=False)

            if recognizer.AcceptWaveform(data):
                result = recognizer.Result()
                text = json.loads(result).get('text', '')
                print(f"You said: {text}")

                if text.lower() == 'command start done':
                    save_chat_history(chat_history)
                    return
                
                if text.lower() == 'eject':
                    if system == 'Linux':
                        os.system(f'unmount /media/{get_user()}/bootloader')

                if text:
                    chat_history.append({'role': 'user', 'content': text})
                    thr = Thread(target=loading)
                    thr.start()

                    response = ollama.chat(model='Zeus', messages=chat_history)
                    isload = 1
                    thr.join()

                    say = response['message']['content']
                    print(say)

                    chat_history.append({'role': 'assistant', 'content': say})

                    save_chat_history(chat_history)
                    ohbot.say(say, lipSync=True)

    except KeyboardInterrupt:
        pass  # Allow clean exit with Ctrl+C

    finally:
        stream.stop_stream()
        stream.close()
        audio.terminate()