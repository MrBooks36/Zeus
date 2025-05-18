from threading import Thread
from ohbotfix import ohbot
import ai
import look
ohbot.reset()
ohbot.detach(ohbot.HEADTURN)
ohbot.detach(ohbot.EYETILT)
ohbot.detach(ohbot.HEADROLL)

thr = Thread(target=look.look, daemon=True)
thr.start()

ai.ai()