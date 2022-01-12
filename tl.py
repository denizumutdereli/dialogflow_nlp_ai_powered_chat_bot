import os
import sys
from googletrans import Translator

def translate(sentence,languageDestination):
	try:
		translator = Translator()
		translate = translator.translate(sentence, languageDestination)
		if translate.text != '':
			return(translate.text)
		else:
			return sentence
	except Exception as e:
		print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
		return False