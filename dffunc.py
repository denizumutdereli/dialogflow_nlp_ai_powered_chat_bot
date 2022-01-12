import df
import tl
import wt
import os
import sys
import codecs
import re
import hashlib
from pathlib import Path
import json
import emoji
import random
import string
from datetime import date
from datetime import datetime
from datetime import timedelta
import time
from rich import print
from rich.pretty import pprint
import winsound
import settings
from bs4 import BeautifulSoup
from sounds import play
import ontology

def dialogReply(core,messagesForApi,lastMessage,customerName,sessionid,account, response, ai = False): #Core functions are temporary. You can fill with your selenium or ide services.

	if response != False:
		try:
			if ai == False:

				#QueryInfo
				outcall_query = response.query_result.query_text
				outcall_parameters = response.query_result.parameters

				#BotRepyInfo
				incoming_reply_id = response.response_id
				incoming_repy = response.query_result.fulfillment_text
				incoming_replies = response.query_result.fulfillment_messages

				#ContextInfo

				incoming_contexts = []
				for context in response.query_result.output_contexts:
					incoming_contexts.append(context)

				#IntentInfo
				incoming_intent = response.query_result.intent.display_name

				incoming_intent_link = response.query_result.intent.name

				incoming_intent_id = incoming_intent_link.split('projects/'+settings.project_id+'/agent/intents/')
				incoming_intent_id = incoming_intent_id[1]

				incoming_intent_confidence = response.query_result.intent_detection_confidence

				incoming_sentiment = response.query_result.sentiment_analysis_result
				# Score between -1.0 (negative sentiment) and 1.0 (positive sentiment).
				if incoming_sentiment.query_text_sentiment:
					score =  round(incoming_sentiment.query_text_sentiment.score,3) * 100
					if score < 0:
						incoming_sentiment = 'Positive: %' +  str(score)
					else:
						incoming_sentiment = 'Negative: %' +  str(score)
				else:
					incoming_sentiment = ''

				botReply = response.query_result.fulfillment_text

			else: #supervised ai in charge!
				botReply = ai
				incoming_intent_confidence = 1
				incoming_intent = 'supervisedAi'
				incoming_intent_id = 0
				incoming_contexts = ''
				incoming_sentiment = 0				

			if botReply != False:

				#Profile Json hashtags!
				botReply = chatCodes(botReply, settings.account) #replace profile json hashtags

				Flag =re.findall('#[a-zA-Z]+', botReply) #SpecialCodesLastCheckForSecurity
				if len(Flag) > 0:
					print('[bold red] I found a new special code but could not change it. [bold yellow]' + Flag[0] + '[/bold yellow], Now passing this conversation. Please check profile json files and Dialogflow! [/bold red]')
					return False

				##ParamsMagic!
				if settings.activeFlow == False and ai == False: #prevent from actions! do not magic
					if 'person' not in outcall_parameters.keys():
						userParams = getParameters(settings.sessionid)
						if userParams != False:
							try:
								userName = userParams.get('name', None)
								userCity = userParams.get('city', None)
								userAge = userParams.get('age', None)
								userCity = userParams.get('city', None)
								wmsg = False
				
								#%10 adding info - TBC only Name right now!
								i = random.randint(0, 50)
								if (i<=50) and userName: #userName approx %10
									nameMagic = ontology.nameMagic(userName)
									if nameMagic != False:
										botReply = str(nameMagic) + ', ' + botReply									
								
								i = random.randint(0, 100) #seperate random to avoid cross cpu calculation buffer bug
								if (i <= 2) and userCity: # %2 for City Magic
									cityMagic = ontology.cityMagic(userCity)
									if cityMagic != False:
										botReply = cityMagic									
							except Exception as e:
								print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
								pass
								
				if settings.translating is True and botReply != '':
					settings.botParams['botReply'] = tl.translate(botReply, settings.translateDestination)
					settings.botParams['lastMessage'] = tl.translate(lastMessage, settings.translateDestination)
				else: 
					settings.botParams['botReply'] = botReply
					settings.botParams['lastMessage'] = lastMessage

				settings.botParams['confidence'] = str(incoming_intent_confidence)
				settings.botParams['intentName'] = str(incoming_intent)
				settings.botParams['intentId'] = incoming_intent_id
				#settings.botParams['context'] = incoming_contexts
				settings.botParams['sentiment'] = str(incoming_sentiment)
 
				return botReply
			else:
				return False
		except KeyError:
			play('alert')
			print('[bold red] Server connection error! Please try again later.. [/bold red]')
			return False
			#print(api_resonse)
			#core.driver.close()
	else:
		print('[bold red] Server connection error! Please try again later.. [/bold red]')
		core.driver.close()

def parameterUpdate(sessionid, parameters, reply): #parameter update is usefull for remembering customer information, lets say after 10 days later you can still remember username and city.
	if len(parameters)>0:
		#Parameters
		info = dict()
		for p,v in parameters.items():
			info[p] = v

		check = 0 #1st person singular
		person = info.get('person',None)
		age = info.get('age',None)
		city = info.get('location', None)

		
		if person or age or city:
			#print('here..')
			#print(info)

			#1st,2ndPerson Controller Fix ##################################### These are german language purpose but you can change it to any language
			FirstPerson = ['mine ', 'mein ', 'meine ', 'ich ', 'das ist ', 'bin ']
			otherPersons = ['meines ','meiner ','sein ','der ', ' er', 'deinem ']

			check = 0
			for first in FirstPerson:
				if first in reply:
					check = 1

			for second in otherPersons:
				if second in reply:
					check = 0
		else:
			return True

		paramCache= {}
		hashFile = str(settings.account)+'_'+hashlib.md5(sessionid.encode("utf-8")).hexdigest() + '.json'
		cacheFile = Path(settings.workingPath + "params/"+hashFile)
		try:
			if cacheFile.is_file():
				with codecs.open(cacheFile, mode='r', encoding='utf-8') as cache:
					paramCache = json.load(cache)

			for param,value in parameters.items():

				#print(param)

				if param == 'person' and check == 1:
					for key,val in value.items():
						if key == 'name':
							paramCache[key] = str(val).capitalize()
				if param == 'person' and check == 0:#2ndPerson
					return False

				if param == 'location' and check == 1:
					#print(3)
					for key,val in value.items():
						if key == 'city':
							paramCache[key] = str(val).capitalize()
				if param == 'location' and check == 0: #2ndPerson
					#print(4)
					return False

				if param == 'age' and check == 1:
					for key,val in value.items():
						if key == 'amount':
							paramCache['age'] = int(val)
				if param == 'age' and check == 0: #2ndPerson
					return False

			if len(paramCache)>0:
				try:
					#print('writing')
					now = datetime.now()
					datetimeFormat = '%Y/%m/%d %H:%M:%S.%f'
					dt_string = now.strftime(datetimeFormat)

					paramCache['account'] =  settings.account
					paramCache['user'] = settings.sessionid
					paramCache['date'] =  dt_string

					with codecs.open(cacheFile, mode='w', encoding='utf-8') as fileToWrite:
						json.dump(paramCache, fileToWrite, sort_keys=False, indent=2, ensure_ascii=False)
					fileToWrite.close()
					return True
				except Exception as e:
					play('alert')
					print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
					return False
			else:
				return True
		except:
			return False
	else:
		return True

def getParameters(sessionid):
	hashFile = str(settings.account)+'_'+hashlib.md5(sessionid.encode("utf-8")).hexdigest() + '.json'
	cacheFile = Path(settings.workingPath + "params/"+hashFile)
	try:
		if cacheFile.is_file():
			with codecs.open(cacheFile, mode='r', encoding='utf-8') as cache:
				paramCache = json.load(cache)
			cache.close()
			return paramCache
		else:
			return False
	except Exception as e:
		print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
		return False

def chatCodes(botReply, account):

	botReply = botReply.replace(",","")
	#prepare the botReply for actions and profile changes
	botKeys = botReply.split(" ")
	try:
		#checkForRestrictedSentences
		if botReply in settings.restrictedsentences['restrictedSentences']:
			print('[bold red]I found forbidden phrases. I am passing![bold red]')
			return False

		#checkProfiles
		for botKey in botKeys:
			if botKey in settings.profiles['profileCodes']:
				botReply = botReply.replace(botKey, settings.profiles['profileCodes'][botKey])
			#checkForSpecialActions
			elif(botKey == '666*'): #could not answer
				print('[bold red]666* code arrived. I am passing![bold red]')
				botReply = False
				break
	except Exception as e:
		play('alert')
		print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
		print('\n[bold red]I got an error while reading profile json files. Please check the files![bold red]')
		#self.driver.close() #spliting bot message is critical and in regards of reason we are closing  the web driver
	finally:
		return botReply