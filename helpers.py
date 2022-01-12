import os
import sys
import re
import emoji
import string
import time
import winsound
from bs4 import BeautifulSoup
from rich.progress import track

def clear():
	os.system('cls' if os.name=='nt' else'clear')

def BeautifulSoupOp(text):
	soup = BeautifulSoup(text.strip(),"html.parser")
	
	for tag in soup.find_all('a'):
		tag.replaceWith('')

	for tag in soup.find_all('span'):
		tag.replaceWith('')

	for tag in soup.find_all('img'):
		tag.replaceWith('')

	text = soup.get_text()

	text = remove_emoji(text)

	return text

def remove_emoji(lastMessage):
	translator = re.compile('[%s]' % re.escape(string.punctuation))
	translator.sub(' ',lastMessage)
	lastMessage = re.sub(r'[^\w\s]', '', lastMessage)

	emoji_pattern = re.compile("["
						   u"\U0001F600-\U0001F64F"  # emoticons
						   u"\U0001F300-\U0001F5FF"  # symbols & pictographs
						   u"\U0001F680-\U0001F6FF"  # transport & map symbols
						   u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
						   u"\U00002702-\U000027B0"
						   u"\U000024C2-\U0001F251"
						   "]+", flags=re.UNICODE)
	lastMessage = emoji_pattern.sub(r'', lastMessage) 
	lastMessage = re.sub(' +',' ', lastMessage).strip()
	return lastMessage

def loading(rangeVal, description):
	#for i in range(25):
		#time.sleep(0.1)
		#sys.stdout.write("\r" + self.loading[i % len(self.loading)])
		#sys.stdout.flush()
	for step in track(range(rangeVal), description=description):
			time.sleep(0.1)
