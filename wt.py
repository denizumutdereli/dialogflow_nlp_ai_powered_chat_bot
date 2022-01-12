import requests
import json
from rich import print

cold = [
	'Es ist kalt in {city} :( ', 
	'Ist es nicht sehr kalt?', 
	'{city} ist immer so kalt', 
	'{city} friert schon wieder :)'
	]
sunny = [
	'Das Wetter in {city} ist nicht schlecht :)',
	'Es ist schönes Wetter in {city}', 
	'schönes Wetter heute.'
	]


def weather(cityName):
	try:
		api_key = "9e172548bccaef3ce4fa810d326e388b"
		url = "https://api.openweathermap.org/data/2.5/weather?q="+cityName+"&units=metric&appid="+api_key
		response = requests.get(url)
		data = json.loads(response.text)
		if data:
			return data
		else:
			return False
	except Exception as e:
		print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
		return False
