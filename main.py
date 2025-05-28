from threading import Thread
from ohbotfix import ohbot
from ai import ai
from look import look
from os.path import exists
import requests
ohbot.reset()
ohbot.detach(ohbot.HEADTURN)
ohbot.detach(ohbot.HEADROLL)

thr = Thread(target=look, daemon=True)
thr.start()

def start_ai(pram):
   try:
    ai(pram)
   except Exception as e:
      with open('ERROR.txt', 'w') as file: 
        file.write(str(e))

def is_site_up(url):
    try:
        response = requests.get(url)
        # If the response status code is less than 400, the site is considered up.
        return response.status_code < 400
    except requests.exceptions.RequestException:
        # If there is any request exception, the site is considered down.
        return False

if not exists('vosk'):
 website_url = "https://www.google.com/speech-api/v2/recognize"
 ohbot.say('Playing ping pong with Larry Page')
 print('Playing ping pong with Larry Page')
 if is_site_up(website_url):
    print(f"{website_url} is up.")
    ohbot.say('connected')
    print('connected')
    start_ai(True)
 else:
    print(f"{website_url} is down.")
    ohbot.say('ha ha i won')
    print('ha ha i won')
    start_ai(False)
else: start_ai(False)