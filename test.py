from abc import abstractclassmethod
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from pathlib import Path
from random import randint
from rich import print
from rich.pretty import pprint
from rich.progress import track
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 
from selenium.webdriver.common.keys import Keys 
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import emoji
import hashlib
import json
import pickle
import requests
import os
import platform
import random
import re
import string
import sys
import subprocess
import time
import warnings
import tl
import df
import ontology
import helpers
import menu
import persona
import nlpgerman
from dffunc import dialogReply
from sounds import play
import settings
import argparse

def testMe():

	# set the hyper-paramters
	parser = argparse.ArgumentParser(description='Help Open:1 / Close:0')
	parser.add_argument('--translate', type=int, default=0, help='Translation Open:1 / Close:0')
	parser.add_argument('--sounds', type=int, default=1, help='Sounds Open:1 / Close:0')
	parser.add_argument('--ai', type=int, default=1, help='Semi-supervised ai Open:1 / Close:0')
	#bunlar geçici!
	parser.add_argument('--account', type=int, default=40, help='Connected Account Id')
	parser.add_argument('--customer', type=str, default='deniz', help='Customer ID for unique Dialogflow conversation')

	args = parser.parse_args()

	helpers.clear()
	helpers.loading(20, '[cyan]Choosing new customer conversation...[/cyan]')
	#Testcake:
	
	lastMessage = input('Client:')
	print("\n")
	
	if lastMessage == '':
		lastMessage = input('Client:')

	#setOptions:

	settings.sounds = args.sounds

	if args.translate == 1:
		settings.translating = True
	else:
		settings.translating = False

	if args.ai == 1:
		settings.supervisedAi = True
	else:
		settings.supervisedAi = False


	if (args.account == ""):
		args.account = 1

	#This section is static and for demo purpose. You can change it with selenium IDE and make it dynamic.###
	#what we need for every loop, first setup customer name and sessionId, track latest messages from conversation and when done go to next conversation.
	#For demo purpose, we will always asked for input as an example to test Dialogflow responses and semi-supervised ai bot to sentimaticly reply.

	customerName = args.customer
	settings.sessionid = hashlib.md5(customerName.encode("utf-8")).hexdigest()
	settings.account = args.account
	lastMessageResponse = {}
	totalMessages = 5
	totalOwnMessages = 1

	#load active bot profile
	try:
		with open(settings.workingPath + '\\profiles\\' +str(settings.account)+'_profile.json') as f:
			settings.profiles = json.load(f)
			#print(settings.profiles)

		with open(settings.workingPath +'\\specials\\codes.json') as f: #with this section you can auto replace hashtags. ie. Hello my name is #botname -> Hello my name is Umut.
				settings.codes = json.load(f)

		with open(settings.workingPath +'\\specials\\restrictedsentences.json') as f: #you may want some of the words should be restricted
			settings.restrictedsentences = json.load(f)
	
	except (OSError, IOError) as e:
		play('alert')
		print("[bold red] I can't read the json files where the profiles are written. There is a problem! [/bold red]")

	#Ontology ########################################################################################

	#checkForFirstCustomer
	if(totalMessages-totalOwnMessages<2): #if customer has one message recently
		print("[bold green]"+customerName+"[/bold green] I found new message [bold blue] auto welcome intents will be triggered: [/bold blue]\n")
		response = ontology.setFlow(settings.sessionid, 'Welcome',1) #flows are easy. You can always handle flows and push to the clients.
		if response != True:
			print("[bold red]Welcome intent could not be triggered!")

	#checkActiveFlow
	activeFlow = ontology.activeFlow(settings.sessionid) #if the customer conversation previously mentioned to a flow. 
	
	if activeFlow != False:
		print("[bold green]"+activeFlow+"[/bold green] is active.\n")
	else:
		print("[bold red]There is no active flow.[/bold red]\n")

	#################################################################################################


	#DF Dialogs and LongMessages NLP sentences ######################################################
	
	print('[cyan]>>>>>>>>> NLP Functions <<<<<<<<<[/cyan]')
	lastMessageNLP = nlpgerman.prepare(lastMessage) #return withResponse / False
	
	if lastMessageNLP == False: #If passed the NLP with blank!
		#print('ok')
		lastMessage = str(lastMessage).strip()
		response = df.detect_intent_texts(settings.sessionid, lastMessage)
	else:
		#print('else')
		lastMessage = lastMessageNLP["main"]
		response = lastMessageNLP["response"]

	#################################################################################################

	if activeFlow != False: #there is an active flow:  !! here we got an answer from dialogflow and the confidence rate is better then our current active flow reply. So active flow will pass for this time.
		#previously check for a better confidence
 
		if response.query_result.intent_detection_confidence >= settings.flowPauseConfidence and 'Default' not in response.query_result.intent.display_name: #reference Settings
			print("[cyan]I found a better confidence. I hold the flow.[/cyan]")
			botReply = dialogReply('','',lastMessage,customerName,settings.sessionid,settings.settings.account,response)
		else:
			print("[cyan]"+activeFlow+" akışı devam ediyor.[/cyan]")
			response = df.detect_intent_texts(settings.sessionid, str(settings.flowTriggerCode)+'_'+ activeFlow)

			#Default Fallback/Welcome Intent in activeFlow response!
			if 'Default' in response.query_result.intent.display_name:
				play("alert")
				print("[red on white]"+activeFlow+" is requested but Dialogflow sending Default Fallback/Welcome Intent. Please check your flow schema and names carefully. [/]")
				input("Enter to continue...")
				return False
			else: #Normal Flow continue
				#EndFlow Check:
				if settings.flowEndCode in response.query_result.fulfillment_text:
					response.query_result.fulfillment_text = response.query_result.fulfillment_text.replace(settings.flowEndCode, '') #clear the flow special codes!
					ontology.endStatus(settings.sessionid) #no return required, param Silent=1
					#flowActions done!)
				elif settings.flowChainCode in response.query_result.fulfillment_text:#chainFlow requested
					flowChain = response.query_result.fulfillment_text.split(settings.flowChainCode)
					response.query_result.fulfillment_text = response.query_result.fulfillment_text.replace(str(settings.flowChainCode)+(flowChain[1]), '') #clear the flow special codes!
					if flowChain[1] and (flowChain[1] in settings.flowStories) or (flowChain[1] in settings.randomStories):
						setFlow = ontology.setFlow(settings.sessionid, str(flowChain[1]),1) #sending chain intent name Force = 1
						time.sleep(1) #atomic conflict
						chainFlow = ontology.activeFlow(settings.sessionid)
						if chainFlow == False:
							print("[bold red]"+chainFlow+" flow chain is requested but I could not open. Please check the settings page and compare with Dialogflow.[/]")
							return False
						else:#chainFlow set
							print("[bold green]"+chainFlow+"[/bold green] is requested and this will be activated on next time.\n")
					else: #chainNotFound
						play("alert")
						print("[red on white]"+str(flowChain[1])+" is requested but I could not open. Please check the settings page and compare with Dialogflow.[/]")
						input("Devam etmek için Enter...")
						pass
				
				botReply = dialogReply('','',lastMessage,customerName,settings.sessionid,settings.account,response) #Flow block okay, now fill the dialogReply

	elif response.query_result.intent.display_name == 'Default Fallback Intent':
		lastMessageAi = persona.askQuestion(lastMessage,settings.account,settings.supervisedAi)
		if lastMessageAi != False:
			botReply = dialogReply('','',lastMessage,customerName,settings.sessionid,settings.account,response,lastMessageAi)
			#else not required due to menu will ask Default intent and and enter the right answer

		elif settings.sendToRandomStories == 1:#reference Settings
			setFlow = ontology.setFlow(settings.sessionid, '') #sending blank intent name will cause random choosing
			randomFlow = ontology.activeFlow(settings.sessionid)
			if setFlow != True:
				print("[bold red]A random "+randomFlow+" stream is requested but I can't open it. Check the settings.!")
				return False
			else:
				print("[bold green]"+randomFlow+"[/bold green] flow was activated randomly.\n")
				response = df.detect_intent_texts(settings.sessionid, str(settings.flowTriggerCode)+'_'+randomFlow)
				response.query_result.fulfillment_text = response.query_result.fulfillment_text.replace(settings.flowEndCode, '') #clear the flow special codes!
				botReply = dialogReply('','',lastMessage,customerName,settings.sessionid,settings.account,response)			
	else: #no one I go normal!
		botReply = dialogReply('','',lastMessage,customerName,settings.sessionid,settings.account,response)
	
	#################################################################################################

	#checkIfAllOkay
	if botReply == False:
		return False

	##all done - starting interaction
	print('\n'+customerName + " (last message): [bold yellow]" + str(settings.botParams['lastMessage']) + "[/bold yellow] ")
	print("YZ: [bold green]" + str(settings.botParams['botReply']) + "[/bold green] ")
	if botReply == '' and str(settings.botParams['intentName']) != '':
		print("[bold red on white] Intent: "+ str(settings.botParams['intentName']) + " I found this Intent but its empty. Please check Dialogflow.[/] ")
		return False
	print('\n-------------------------------------------------------------')
	print("[cyan]Confidence:[/cyan]  " + str(settings.botParams['confidence']))
	print("[cyan]Intent: [/cyan]" + str(settings.botParams['intentName']))
	print("[cyan]IntentId: [/cyan]" + str(settings.botParams['intentId']))
	print("[cyan]Pos/Neg:[/cyan]  " + str(settings.botParams['sentiment'])) #sentiment analysis

	#alert for bad sentiment
	if 'Negative' in str(settings.botParams['sentiment']):
		ontology.alertStatus(settings.sessionid)

	#Load menu functions: ###############################################################################
	answer = menu.typeOfAction('',str(settings.botParams['intentName']))
 
	if(answer is True):		
		#ALL done sending message - sandbox!
		#helpers.loading(10, '[cyan]Sharing begins...[/cyan]')
		#messageText = self.driver.find_element_by_id('mod_message_'+str(settings.account))
		
		if settings.humanLikeWrite == 1:
			botReply = ontology.wrongWriting(botReply)
		
		#messageText.send_keys(botReply)
		helpers.loading(30, '[cyan]I am sending the message...[/cyan]')
		#WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.ID, "message_send_button_"+str(settings.account))).click()
		play('sent')
		print('[bold green]I sent the message![/bold green]')
		time.sleep(1)
		time.sleep(2)
		testMe()

	elif(answer is False):
		time.sleep(2)
		testMe()
	elif answer in ['$tlclose','$tlopen']:
		if answer == '$tlopen':
			settings.translating = True
			helpers.loading(10, '[cyan]Opening translation...[/cyan]')
		else:
			settings.translating = False
			helpers.loading(10, '[cyan]Closing translation...[/cyan]')
		time.sleep(2)
		testMe() #refresh the chat
	elif answer in ['$snopen','$snclose']:
		if answer == '$snopen':
			settings.alertSounds = 1
			helpers.loading(10, '[cyan]Opening sounds..[/cyan]')
		else:
			settings.alertSounds = 0
			helpers.loading(10, '[cyan]Closing sounds..[/cyan]')
		time.sleep(2)
		testMe() #refresh the chat
	elif answer in ['$refresh', '$exit']:
		helpers.loading(10, '[cyan]Refreshing the conversation...[/cyan]')
		time.sleep(2)
		testMe() #refresh the chat
	elif answer == '$quit': #shutdown requested
		helpers.loading(10, '[cyan]Exit requested...[/cyan]')
		play('alert')
		confirm = menu.yes_or_no('Are you really want to leave?')
		if confirm == True:
			print('software exit!')
			time.sleep(2)
		else:
			helpers.loading(10, '[cyan]Exit cancelled...[/cyan]')
			time.sleep(2)
			testMe() #refresh the chat
	elif len(answer) > 0: #training requested
		intentTraining(settings.account, lastMessage, answer['intentName'],answer['botReply'])
		#print(answer)


def intentTraining(account, lastMessage, intentName, botReply):
	try:
		soup = BeautifulSoup(botReply.strip(),"html.parser")
		botReply = soup.get_text()

		lastMessage = helpers.remove_emoji(lastMessage)

		botReply = botReply.replace(';','') #delimeterConflicts
		lastMessage = lastMessage.replace(';','') #delimeterConflicts

		#checkIfTheIntentExist
		intent_id = df.get_intent_id(intentName.strip())

		if intent_id == False or intent_id =='': #no intent found - create a new one!
			create = df.create_intent(intentName, [lastMessage], [botReply])
			if create != False:
				print('[bold green] Intent: ' + intentName + ' has been created!')
			else:
				print('[bold red] Intent: ' + intentName + ' could not be created! Check for the settings and the error logs. [/bold red] @admin')
				return False
		else:
			update = df.update_intent(intent_id, [lastMessage], botReply)
			if update != False:
				print('[bold green] Intent: ' + intentName + ' name found and I have updated it.[/bold green]')
			else:
				print('[bold red] Intent: ' + intentName + ' name found but I could not update it! Check for the settings and the error logs.[/bold red]')
				print('[black on white]Hint: FlowUpIntent loops can not be changed from CLI. You can write an another name and continue...[/]')
				intentName = menu.askIntentName('Please enter an another Intent name:')
				return intentTraining(settings.account,lastMessage,intentName,botReply)
		#alldone-nowsendthemessage!
		persona.train(botReply,settings.account) #semisupervisedLearning

		print('Send message after training!')
		time.sleep(2)
		testMe()

	except Exception as e:
		play('alert')
		print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
		print('[bold red] Communication error with server! [/bold red]')
		print('error exit')
  
testMe()