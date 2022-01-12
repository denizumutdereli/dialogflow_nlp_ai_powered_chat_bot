import os
import sys
import settings
#import google.cloud.dialogflow_v2 as dialogflow_v2
from google.cloud import dialogflow as dialogflow_v2
from google.protobuf import field_mask_pb2

from rich import print
import dffunc as dff #special!

def get_intent_id(display_name):
	try: 
		intents_client = dialogflow_v2.IntentsClient()
		parent = dialogflow_v2.AgentsClient.agent_path(settings.project_id)
		intents = intents_client.list_intents(request={"parent": parent})

		intent_names = [
			intent.name for intent in intents if intent.display_name == display_name
		]

		intent_ids = [intent_name.split("/")[-1] for intent_name in intent_names]
		if len(intent_ids) != 0:
			return(intent_ids[0])
		else:
			return False
	except Exception as e:
		#print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
		return False    

def getIntent(intent_id): 
	try:
		client = dialogflow_v2.IntentsClient()
		intent_name = client.intent_path(settings.project_id, intent_id)
		intent = client.get_intent(request={"name": intent_name})
		return intent;
	except Exception as e:
		print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
		return False

def create_intent(display_name, training_phrases_parts, message_texts):
	try:
		intents_client = dialogflow_v2.IntentsClient()

		parent = dialogflow_v2.AgentsClient.agent_path(settings.project_id)
		training_phrases = []
		for training_phrases_part in training_phrases_parts:
			part = dialogflow_v2.Intent.TrainingPhrase.Part(text=training_phrases_part)
			# Here we create a new training phrase for each provided part.
			training_phrase = dialogflow_v2.Intent.TrainingPhrase(parts=[part])
			training_phrases.append(training_phrase)

		text = dialogflow_v2.Intent.Message.Text(text=message_texts)
		message = dialogflow_v2.Intent.Message(text=text)

		intent = dialogflow_v2.Intent(
			display_name=display_name, training_phrases=training_phrases, messages=[message],webhook_state = 'WEBHOOK_STATE_ENABLED'
		)

		response = intents_client.create_intent(
			request={"parent": parent, "intent": intent}
		) 
	except Exception as e:
		#print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
		return False    

def changeIntentName(intent_id, newName):
	try:
		client = dialogflow_v2.IntentsClient()
		
		intent_name = client.intent_path(settings.project_id, intent_id)
		intent = client.get_intent(request={"name": intent_name})

		intent.display_name = newName
		update_mask = field_mask_pb2.FieldMask(paths=["display_name"])
		response = client.update_intent(intent=intent, update_mask=update_mask, language_code=settings.language_code)
		return response
	except Exception as e:
		print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
		return False

def update_intent(intent_id, training_phrases_parts,message_texts):
	try:
		client = dialogflow_v2.IntentsClient()
		intent_name = client.intent_path(settings.project_id, intent_id)
		intent = client.get_intent(request={"name": intent_name})
		training_phrases = []
		for training_phrases_part in training_phrases_parts:
			part = dialogflow_v2.Intent.TrainingPhrase.Part(
				text=training_phrases_part)
			training_phrase = dialogflow_v2.Intent.TrainingPhrase(parts=[part])
			training_phrases.append(training_phrase)
		intent.training_phrases.extend(training_phrases) 
		intent.messages[0].text.text.append(message_texts)
		update_mask = field_mask_pb2.FieldMask(paths=["display_name","training_phrases","messages"])
		response  = client.update_intent(intent=intent, update_mask=update_mask, language_code=settings.language_code)
		return response
	except Exception as e:
		print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
		return False

def delete_intent_logic(intent_id):
	try:
		#finding Intent Id
		intent_id = get_intent_id(intent_id)
		if intent_id != False:
			deleteIntent = delete_intent_function(intent_id)
			if deleteIntent != False:
				return True
			else:
				return False
		else:
			return False
	except Exception as e:
		#print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
		return False			

def delete_intent_function(intent_id):
	try:
		 
		intents_client = dialogflow_v2.IntentsClient()

		intent_path = intents_client.intent_path(settings.project_id, intent_id)

		response = intents_client.delete_intent(request={"name": intent_path})
		
		if response == '':
			return False
		else:
			return True

	except Exception as e:
		#print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
		return False

def detect_intent_texts(session_id, text, ai = False):
	try:
		if ai != False:
			text = 'aiHello' #bypass
		#ApiConnection
		session_client = dialogflow_v2.SessionsClient()
		session = session_client.session_path(settings.project_id, session_id)
		text_input = dialogflow_v2.TextInput(text=text, language_code=settings.language_code)
		query_input = dialogflow_v2.QueryInput(text=text_input)
		response = session_client.detect_intent(session=session, query_input=query_input)

		if response == '':
			return False
		else:
			outcall_parameters = response.query_result.parameters
			firstPerson = dff.parameterUpdate(settings.sessionid,outcall_parameters,text) #update Parameters
			if firstPerson:
				return response	
			else:
				#print(0)
				return detect_intent_texts(session_id, settings.defaultIntentFallback)
	except Exception as e:
		print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
		return False

def flowup_input(session_id, inputName):
	try:
		#ApiConnection
		session_client = dialogflow_v2.SessionsClient()
		session = session_client.session_path(settings.project_id, session_id)
		event_input = dialogflow_v2.EventInput(name=inputName, language_code=settings.language_code)
		query_input = dialogflow_v2.QueryInput(event=event_input)
		response = session_client.detect_intent(session=session, query_input=query_input)

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

		return response
	except Exception as e:
		print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
		return False

def train_agent():
	try:
		agents_client = dialogflow_v2.AgentsClient()
		parent = dialogflow_v2.AgentsClient.common_project_path(settings.project_id)
		response = agents_client.train_agent(request={"parent": parent})
		return response.done()
	except Exception as e:
		#print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
		return False

#text = 'what is your name?'
#detect_intent_texts('testbot-mldq', 'abc123', text, 'de')
#flowup_input('testbot-mldq', 'abc123', 'goygoy', 'de')
#getIntent('testbot-mldq','633debaa-6680-4108-b94b-499761d3300f')
#changeIntentName('testbot-mldq','633debaa-6680-4108-b94b-499761d3300f','ladung')
#update_intent('testbot-mldq','633debaa-6680-4108-b94b-499761d3300f', ['birinci cümle','ikinci cümle', 'üçüncü cümle'], 'yok bir sey!')
#train_agent('testbot-mldq')
#delete_intent_function('testbot-mldq','6a68b930-664e-4790-9c37-61ac2fc82e14')
#create_intent('testbot-mldq', 'deniz4@deniz', ['Başka bir cümle daha ekleyelim', 'İkinci ve farklı bir cümle daha ekleyelim'], ['yeni bir cevar versin mi?'])
#delete_intent_logic('testbot-mldq', 'deneme');
#train_agent('testbot-mldq')