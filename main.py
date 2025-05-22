from threading import Thread
from ohbotfix import ohbot
import ai
import look
from os import system
ohbot.reset()
ohbot.detach(ohbot.HEADTURN)
ohbot.detach(ohbot.HEADROLL)

thr = Thread(target=look.look, daemon=True)
thr.start()

ohbot.say('Playing ping pong with Larry Page')
ping = system('ping speech.googleapis.com')
if ping == 0:
    ohbot.say('connected')
    ai.ai(True)
else:
    ohbot.say('ha ha i won')
    ai.ai(False)
