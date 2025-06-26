from ai import ai
from os.path import exists


def start_ai(pram):
   try:
    ai(pram)
   except Exception as e:
      with open('ERROR.txt', 'w') as file: 
        file.write(str(e))

if not exists('vosk'): start_ai(True)
else: start_ai(False)