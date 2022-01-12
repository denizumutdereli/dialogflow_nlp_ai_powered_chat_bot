import os
import sys
import re
import hashlib
import json
import string
import time
import winsound
import tl
import df
import settings
import helpers
import ontology
from pathlib import Path
from rich import print
from bs4 import BeautifulSoup
from rich.progress import track
from sounds import play

def yes_or_no(question):
	prompt = f'{question} (e/h): '
	answer = input(prompt).strip().lower()
	if answer not in ['e', 'h']:
		print(f'{answer} this answer is not correct, can you answer again...')
		return yes_or_no(question)
	if answer == 'e':
		return True
	elif answer == 'h':
		return False

def typeOfAction(core,intentName):
	#Type of Actions for the terminal
	print("\n[bold magenta] ######## LEARN MODE ON: ########[/bold magenta]")
	print("\n[green on white] e: SHARE THIS MESSAGE[/]")
	print("[bold red on white] h: NO SHARE[/]")
	print("[bold blue on white] t: SAVE A NEW SENTENCE[/]")
	print("[bold black on white] a: START A NEW FLOW[/]")
	print("[bold magenta on white] s: DELETE THIS INTENT[/]")

	print('[bold magenta]____________________________________________[/bold magenta]')

	prompt = '\nPlease select an action: (e/h/t/s/a): '
	answer = input(prompt).strip().lower()
	if answer not in ['e', 'h', 't', 's', 'a', '$tlclose', '$tlopen','$snopen', '$snclose', '$refresh','$quit']:
		print(f'{answer} this answer is not correct, can you answer again...')
		return typeOfAction(core,intentName)
	if answer == 'e':
		answer = yes_or_no('It will be shared. Can you confirm again?:')
		if intentName != 'Default Fallback Intent' and answer == True:
			intentScore = investigateIntent(intentName, 1)
			if intentScore < -10:
				poortAction = poorIntent(intentName,intentScore) #excluded from loop
		return answer #True/False from yes_or_no
	elif answer == 'h':
		if intentName != 'Default Fallback Intent':
			intentScore = investigateIntent(intentName, -1)
			if intentScore < -10:
				poorAction = poorIntent(intentName,intentScore) #excluded from loop
		return False
	elif answer in ['$tlclose', '$tlopen','$snopen', '$snclose', '$refresh', '$quit']:
		return answer
	elif answer == 'a':
		print("\n[bold blue] ######## Stream Mode On: ########[/bold blue]  [blue](You can type $exit to exit)[/blue]")
		return flowTerminal(core,'Please type the name of the stream you want to forward:')
	elif answer == 's':
		print("[bold red] ######## ATTENTION THIS INTENT/STATUS WILL BE DELETED: ########[/bold red]  [blue](You can type $exit to exit)[/blue]")
		deleteConfirm = yes_or_no(str(intentName) + ' You wanted it deleted. Can you confirm?')
		if deleteConfirm == True and intentName != "":
			delete  = df.delete_intent_logic(settings.project_id, str(intentName))
			if delete:
				print('[cyan] '+ str(intentName)+' deleted! [/cyan]')
			else:
				print('[red]' + str(intentName) + ' could not be deleted. Can you try again later? Let me know if it is still not deleted.')
				input('ENTER to continue...')
		elif (intentName == ""):
			return '$refresh'
		return '$refresh'
		
	elif answer == 't':
		print("\n[bold blue] ######## Development Mode On: ########[/bold blue]")
		if settings.translating is True:
			print('\n[red on white]DİKKAT[/][black on white] Translation is open. You can write in '+settings.translateDestination+', I will translate it into German.[/]\n')	
		return trainingTerminal(core,'Please write the sentence you want to record:')

def trainingTerminal(core,question):
	#Type of Actions for the terminal	
	prompt = f'{question}'
	botReply = input(prompt).strip()
	Flag =re.findall('#[a-zA-Z]+', botReply) #FlagName = Um:

	if len(botReply) == 0:
		return trainingTerminal(core,'How would artificial intelligence respond to this more accurately?:')
	elif botReply == '$exit':
		return False
	elif botReply in ['$tlopen', '$tlclose','$snopen', '$snclose', '$refresh', '$quit']:
		return botReply
	elif len(botReply) > 150:
		return trainingTerminal(core,'Could you write a slightly shorter answer? (max 150 characters):')
	elif len(botReply) < 10:
		return trainingTerminal(core,'Can you write a slightly longer answer? (min 10chars):')
	elif len(Flag) > 0:
		return trainingTerminal(core,'Currently we cannot use special codes like '+Flag[0]+' in answers. Can you write again:')
	else:
		if settings.translating is True:
			print('[bold red]'+str(settings.translateDestination) + '[/bold red]:[cyan]' + botReply + '[/cyan]')
			botReply = tl.translate(botReply, settings.language_code)
			print('[bold green]'+str(settings.language_code) + '[/bold green]:[cyan]' + botReply + '[/cyan]')
		confirm = yes_or_no('Let AI write :\n'+botReply +' is it true?')
		if confirm == True:
			response = {}		
			#nowAskIntentName
			if settings.translating is True:
				print('\n[black on white]It does not matter what language the intent names are written in. You can give it a name in any language you want.[/]\n')	
			intentName = askIntentName(core,'Type an intent name:')
			
			if intentName in ['$tlclose', '$tlopen','$snopen', '$snclose', '$refresh', '$quit','$exit']:
				return intentName
			elif intentName != False:
				response['botReply'] = botReply
				response['intentName'] = intentName
				return response
			else:
				return False #cancelled
		else:
			return trainingTerminal(core,'How would artificial intelligence respond to this more accurately?:')

def askIntentName(core,question):
	prompt = f'{question}'
	intentName = input(prompt).strip()
	Flag =re.findall('#[a-zA-Z]+', intentName) #FlagName = Um:

	if len(intentName) == 0:
		return askIntentName(core,'Type an intent name and send the message:')
	elif intentName in ['$tlclose', '$tlopen','$snopen', '$snclose', '$refresh', '$quit','$exit']:
		return intentName
	elif len(intentName) > 50:
		return askIntentName(core,'Can you write a slightly shorter status/intent name? (max 50 characters):')
	elif len(intentName) < 2:
		return askIntentName(core,'Can you write a slightly longer status/intent name? (min 2 characters):')
	elif len(Flag) > 0:
		return askIntentName(core,Flag[0]+' We cannot use special codes in status/intent names. Can you write again?:')
	else:
		confirm = yes_or_no('Status/Intent name will be :\n'+intentName + ' correct?')
		if confirm == True:
			confirm = intentName
			return confirm
		else:
			return askIntentName(core,'Write a status/intent name and send the message:')

def poorIntent(intentName,intentScore):
	print("\n[bold red] ######## WEAK INTENT WARNING: ########[/bold red]")
	print("[bold red on white]The intent named "+intentName+" " +str(intentScore)+ " is causing too many errors with the score.[/]")
	prompt = '\nremove this intent?: (e/h): '
	answer = input(prompt).strip().lower()
	if answer not in ['e', 'h']:
		print(f'{answer}This answer is not correct, can you answer again...')
		return poorIntent(intentName,intentScore)
	if answer == 'e':
		deleteIntent = yes_or_no('Intent is being removed. Can you confirm again?:')
		if deleteIntent == True:
			deleteIntent = df.delete_intent_logic(settings.project_id, intentName)
			if deleteIntent == True:
				#Remove cache file
				fileRemove = removeIntentScoreFile(intentName)
				if fileRemove == True:
					print("\n[blue on white] Removed "+intentName+" status/intent. I continue.[/]")
					time.sleep(2)
					return True
				else:
					print("\n[red on white] Failed to remove status/intent cache file "+intentName+". There is a problem. Please inform. I am continuing for now.[/]")
					time.sleep(2)
					return False
			else:
				print("\n[red on white] Failed to remove status/intent "+intentName+". There is a problem[2]. Please inform. I am continuing for now.[/]")
				time.sleep(2)
				return False
		else:
			print("\n[blue on white] Intent removal aborted. I continue.[/]")
			time.sleep(2)
			return False

	elif answer == 'h':
		print("\n[blue on white] Intent removal aborted. I continue.[/]")
		time.sleep(2)
		return False

def investigateIntent(intentName,score):
	intentNameHash = hashlib.md5(intentName.encode("utf-8")).hexdigest()
	intentCheckFile = Path(settings.workingPath + "intents/"+intentNameHash+'.json')

	correct = 0
	fail = 0

	if score > 0:
		correct = 1
	else:
		fail = 1

	if intentCheckFile.is_file():
		with open(intentCheckFile) as cache:
			intentCache = json.load(cache)

			scores = intentCache['scores']

			failScore = scores[1]['score']['fail']
			correctScore = scores[1]['score']['correct']
			#updateScore
			failScore = int(failScore) + int(fail)
			correctScore = int(correctScore) + int(correct)

			#updateFile
			cacheToWrite = {}
			cacheToWrite['scores'] = []
			cacheToWrite['scores'].append({'intentName': str(intentName)})
			cacheToWrite['scores'].append({'score' : { 'correct': int(correctScore), 'fail' : int(failScore)} })
			with open(intentCheckFile, 'w') as fileToWrite:
				json.dump(cacheToWrite, fileToWrite, indent=4, sort_keys=True, ensure_ascii=False)
	else:
		cacheToWrite = {}
		cacheToWrite['scores'] = []
		cacheToWrite['scores'].append({'intentName': str(intentName)})
		cacheToWrite['scores'].append({'score' : { 'correct': int(correct), 'fail' : int(fail)} })
		correctScore = correct
		failScore = fail
		with open(intentCheckFile, 'w') as fileToWrite:
			json.dump(cacheToWrite, fileToWrite, indent=4, sort_keys=True, ensure_ascii=False)

	#intent success calculation basic
	response = correctScore - failScore #correct - if the error drops to less than minus 10 even when the errors are removed, the intent deletion menu is displayed.

	return response

def removeIntentScoreFile(intentName):
	intentNameHash = hashlib.md5(intentName.encode("utf-8")).hexdigest()
	intentFilePath = settings.workingPath + "intents/"+intentNameHash+'.json'
	if os.path.isfile(intentFilePath):
		os.remove(intentFilePath)
		return True
	else:
		return False


def flowTerminal(core,question):
	#Type of Flows for the terminal
	intentFlow = let_user_pick(core,settings.flowStories)
	if intentFlow in ['$tlopen', '$tlclose','$snopen', '$snclose', '$refresh', '$quit', '$exit']:
		return intentFlow
	elif intentFlow == '$end':
		endFlow = ontology.endStatus(settings.sessionid)
		if endFlow == True:
			return '$refresh'
		else:
			return endFlow
	elif intentFlow != False:
		setFlow = ontology.setFlow(settings.sessionid,intentFlow,force=0)
		if setFlow == True:
			return '$refresh'
		else:
			return setFlow


def let_user_pick(core,options):
	print("\n[blue on white]------- Selectable Features: -------[/]\n")
	for idx, element in enumerate(options):
		print("{}) {}".format(idx+1,element))
	i = input("\nPlease write the number you see on the left: ")

	if i in ['$tlopen', '$tlclose','$snopen', '$snclose', '$refresh', '$quit', '$exit','$end']:
		return i
	elif not i.isdigit():
		let_user_pick(core,options)
	else:
		if (int(i)<=len(options) and int(i) > 0):
			answer = yes_or_no(options[int(i)-1] + ' selected. Can you confirm again?:')
			if answer == True:
				#print(options[int(i)-1])
				return str(options[int(i)-1]) #choosen FlowName!
			else:
				let_user_pick(core,options)
		else:
			let_user_pick(core,options)