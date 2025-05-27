from threading import Thread
from ohbotfix import ohbot
from . import ai, look
ohbot.reset()
ohbot.detach(ohbot.HEADTURN)
ohbot.detach(ohbot.HEADROLL)

thr = Thread(target=look, daemon=True)
thr.start()

import requests

def is_site_up(url):
    try:
        response = requests.get(url)
        # If the response status code is less than 400, the site is considered up.
        return response.status_code < 400
    except requests.exceptions.RequestException:
        # If there is any request exception, the site is considered down.
        return False

website_url = "https://speech.googleapis.com"
ohbot.say('Playing ping pong with Larry Page')
if is_site_up(website_url):
    print(f"{website_url} is up.")
    ohbot.say('connected')
    ai(True)
else:
    print(f"{website_url} is down.")
    ohbot.say('ha ha i won')
    ai(False)
