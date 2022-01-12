import os
import sys

#System
workingPath = os.path.dirname(os.path.realpath(__file__)) + '/' #system
driverLink = workingPath + 'driver/chromedriver.exe' #system
#userDataDir = 'C:\\selenium\\UserData' #system
url = "http://yoursite.com/api" #system Example url for your selenium ide. Or your API url.
messengerLink = "http://yoursite.com/messenger" #system. Example API endpoint or selenium conversation tracking page
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '1' #system
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = workingPath+'certificate/your_certificate.json' #google certicates system
profiles = '' #system
codes = '' #system
restrictedsentences = '' #system
confidence = '' #system
intentName = '' #system
project_id = "testbot-mldq" #system Google Dialogflow project id
language_code = 'de' #system
botParams = {} #system
account = ''
sessionid = ''
#Changeable
defaultIntentFallback = 'ich küsse dich :*'
supervisedAi = True #ai speak it self. set True to open False to close!
supervisedAi_confidence = 0.1 #confidence check for supervised ai
personaFile = ''
sendToRandomStories = 1 #sends to random stories, disable it with set 0
flowStories = ['FirstWelcome','feelBad','feelGood', 'talkCasual', 'talkSport', 'cityTalk']
randomStories = ['RandomFlowUp'] #severalTimes!
flowTriggerCode = '$$call_'
flowEndCode = '$$endFlow'
flowChainCode = '$$chain_'
flowPauseConfidence =0.5
activeFlow = False
flowCacheTimeInMinutes = 120 #system 240 minutes
humanLikeWrite = 1 #For humanoid spelling, there is an 8% probability that a sentence will misspell 1 letter if it has at least more than 25 letters. 0 to turn off
wrongWritingLettersCount = 100 #information about how many letters will be misspelled.
translating = False #translation mode on/off True on, False off
translateDestination = 'tr'  #What language will the translation be in?
alertSounds = 1 #turn off sounds 1/0
accounts = ['1','2'] #chatbot IDS - dom elements or API keywords in which you way you want not to connect your bots. The more ids you define, the more bots you will have.



