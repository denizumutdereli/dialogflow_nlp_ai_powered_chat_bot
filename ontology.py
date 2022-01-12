import os
import sys
import re
import codecs
import hashlib
import json
import string
import time
import winsound
import menu
import tl
import wt
import df
import settings
import helpers
import random
import rich
from documentRetrievalModel import documentRetrievalModel as DRM
from processedQuestion import processedQuestion as PQ
from rich.pretty import pprint
from datetime import date
from datetime import datetime
from datetime import timedelta
from pathlib import Path
from rich import print
from bs4 import BeautifulSoup
from rich.progress import track
from sounds import play
from string import ascii_letters

def setFlow(sessionid,flowIntentName,force=0):
	if flowIntentName == '':
		flowIntentName = random.choice(settings.randomStories)


	#checkForDublicateFlowRequest
	flowName = activeFlow(sessionid)
	if flowName == flowIntentName:
		print('[bold green]'+flowIntentName+' is active.[/bold green]')
		return False

	response = df.flowup_input('sysSession', flowIntentName) #sending sysSession for dummy to check the flowUp input is exist!
	if response == False:
		return False
	else:
		if response.query_result.action != 'input.unknown':
			#pprint(response)
			now = datetime.now()
			datetimeFormat = '%Y/%m/%d %H:%M:%S.%f'
			dt_string = now.strftime(datetimeFormat)

			#startFlowFortheCustomer
			flowFile = Path(settings.workingPath + "flows/"+sessionid+'.json')

			if force == 1: #force to change feeling now.
				flowCache = {}
				flowCache['flows'] = []
				flowCache['flows'].append({'action': flowIntentName, 'count':1, 'date':dt_string})
				with codecs.open(flowFile, mode='w',encoding='utf-8') as fileToWrite:
					json.dump(flowCache, fileToWrite, indent=4, sort_keys=True, ensure_ascii=False)
				fileToWrite.close()
				print('[bold green]'+flowIntentName+' selected and updated.[/bold green]')
				return True
			else:
				if flowFile.is_file():
					with codecs.open(flowFile, mode='r',encoding='utf-8') as cache:
						flowCache = json.load(cache)
						#searchForTheSameFeeling
						cursor = 0
						count = len(flowCache['flows'])

						if count > 0:
							for flow in flowCache['flows']:
								actionName = flow['action']
								actionDate = flow['date']
							
							time_dif = datetime.strptime(dt_string, datetimeFormat) - datetime.strptime(actionDate,datetimeFormat)
							minues_dif = round(time_dif.total_seconds() /60)
							if minues_dif < settings.flowCacheTimeInMinutes: #if bigger then 60*60*24 update counter	
								print('\n[red on white]Caution! '+flowIntentName+' is requested however '+str(minues_dif)+' minutes ago '+actionName+' flow has been activated.[/]')
								play('alert')
								update = menu.yes_or_no("Are you sure, you want to change?")
								if update == False:
									return False
								else:
									#update with Force
									return setFlow(sessionid,flowIntentName,force=1) #FORCE 1
							else: #no active flow - write a new one!
								flowCache = {}
								flowCache['flows'] = []
								flowCache['flows'].append({'action': flowIntentName, 'count':1, 'date':dt_string})
								with codecs.open(flowFile, 'w',encoding='utf-8') as fileToWrite:
									json.dump(flowCache, fileToWrite, indent=4, sort_keys=True, ensure_ascii=False)
								fileToWrite.close()
								print('[bold green]'+flowIntentName+' selected and added.[/bold green]')
								return True
				else:
					flowCache = {}
					flowCache['flows'] = []
					flowCache['flows'].append({'action': flowIntentName, 'count':1, 'date':dt_string})
					with codecs.open(flowFile, mode='w',encoding='utf-8') as fileToWrite:
						json.dump(flowCache, fileToWrite, indent=4, sort_keys=True, ensure_ascii=False)
					fileToWrite.close()
					print('[bold green]'+flowIntentName+' selected and added.[/bold green]')
				return True
		else:
			play('alert')
			print('\n[red on white]Caution! '+flowIntentName+' flow name requested however I could not find this at Dialogflowd.![/]')
			input("Please enter to continue...")
			return False
		#rastgele ruh hali

def activeFlow(sessionid):
	now = datetime.now()
	datetimeFormat = '%Y/%m/%d %H:%M:%S.%f'
	dt_string = now.strftime(datetimeFormat)

	#startFlowFortheCustomer
	flowFile = Path(settings.workingPath + "flows/"+sessionid+'.json')

	if flowFile.is_file():
		with codecs.open(flowFile, mode='r',encoding='utf-8') as cache:
			flowCache = json.load(cache)
			#searchForTheSameFeeling
			cursor = 0
			for flow in flowCache['flows']:
				time_dif = datetime.strptime(dt_string, datetimeFormat) - datetime.strptime(flow['date'],datetimeFormat)
				minues_dif = round(time_dif.total_seconds() /60)
				if minues_dif < settings.flowCacheTimeInMinutes: #if bigger then 60*60*24 update counter
					settings.activeFlow = flow['action']
					return flow['action']
				else:
					return False
		cache.close()
	else:
		return False #noFlowsCurrently

def endStatus(sessionid):
	#startFlowFortheCustomer
	flowFile = Path(settings.workingPath + "flows/"+sessionid+'.json')
	if flowFile.is_file():
		print('\n[red on white]Caution! Message received for termination of flow. I am deleting the stream info.[/]')
		try:
			os.unlink(flowFile)
			settings.activeFlow = False
			return True
		except:
			play('alert')
			print('\n[red on white]Attention! I have been asked to terminate the stream but I can not cancel it. It has to be canceled manually![/]')
			return False
	else:
		print('\n[red on white]Attention! I haveve been asked to terminate the stream but I can not cancel it. It has to be canceled manually![/]')
		settings.activeFlow = False #doubleCheck
		return True #noFlowsCurrently
	#konuşmanın sonlanması

def alertStatus(sessionid):
	print('\n[red on white]Attention! There is something negative about this conversation.[/]')
	play('alert')
	input("Enter to continue...")
	return True
	#Umutu uyar.

def wrongWriting(text):
	i = random.randint(0, 25)
	if i<2: #%8 possibility
		if len(text) > 25:
			inds = [i for i,_ in enumerate(text) if not text.isspace()]
			sam = random.sample(inds, settings.wrongWritingLettersCount) #count of letters to change
		
			lst = list(text)

			for ind in sam:
			    lst[ind] = random.choice(ascii_letters)

			text = "".join(lst)
			print('\n[blue on white]Humanoid spelling is active, I am intentionally misspelling ' + settings.wrongWritingLettersCount + 'letters. Don not panic :)[/]')
	return text.lower()
	#hatalı yazma

def cityMagic(city): #TBC for now only weather
	wmsg = False
	weather = wt.weather(str(city))
	if weather:
		ct = weather['main']['temp']
		if ct <= 10:
			wmsg = random.choice(wt.cold)
			wmsg = wmsg.replace('{city}', str(city))
		elif ct >= 20:
			wmsg = random.choice(wt.sunny)
			wmsg = wmsg.replace('{city}', str(city))
	return wmsg

def nameMagic(name): #TBC It is necessary to see if it is saying the first person singular name or someone else's name.
	if name:
		return name
	else:
		return False


def smartTalk():
	a=1

def timeSpecial(sessionid):
	badFlows = settings.badFlows
	response = df.flowup_input(settings.project_id, sessionid, feelingIntentNames, settings.language_code)
	if response.query_result.action != 'input.unknown':
		pprint(response)
		return response
	else:
		print('\n[red on white]Caution! '+feelingIntentNames+' I was asked to mood talk but I could not find these settings in Dialogflow![/]')
		return False
	#time-distinguished flows or conditions