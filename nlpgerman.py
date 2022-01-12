import os
import sys
import json
import spacy
from rich import print
from rich.pretty import pprint
from spacy.lang.de import German 
from spacy.lang.de.examples import sentences
from nlpclass import ClausedSentence
import df
import settings
from sounds import play

#nlp = spacy.load("de_core_news_sm")
nlp = spacy.load("de_core_news_md")
#nlp = spacy.load('de_core_news_lg')
#nlp = German()
#nlp.add_pipe('sentencizer')

def split_in_sentences(text):
	try:
		document = nlp(text)
		sentences = document.sents

		for sentence in sentences:
			claused_sentence = ClausedSentence(sentence.doc, sentence.start, sentence.end)
			
			clauses = list(claused_sentence.clauses)
			
			extract = {}
			extract['MAIN'] = []
			extract['SUB'] = []

			for clause in clauses:
				if clause.clause_type == 'MAIN':
					extract['MAIN'].append(clause.inner_spans)
				else:
					extract['SUB'].append(clause.inner_spans)

				#print(f"{clause.clause_type}: {clause.inner_spans}")
		return extract
	except Exception as e:
		#print(e)
		return False

def prepare(lastMessage):
	lastMessageTemp = dict()
	try:
		sentences = split_in_sentences(lastMessage)
		if sentences != False:
			pprint(sentences)
			print()
			confidence = 0
			#pprint(sentences)
			#main and sub sentences
			if len(sentences) > 0 and len(sentences['MAIN'])>0:
				i=0
				for i in range(len(sentences['MAIN'])):
					sentencesMain = sentences['MAIN'][int(i)]
					i+=1
					for sentence in sentencesMain:
						lastMessage = str(sentence).strip()
						response = df.detect_intent_texts(settings.sessionid, lastMessage)
						if response.query_result.intent.display_name != 'Default Fallback Intent' and response.query_result.intent_detection_confidence > (confidence): #choose better confidence
							#print(lastMessage, response.query_result.intent.display_name, response.query_result.intent_detection_confidence)
							#lastMessageTemp['sentences'].append({'main':lastMessage, 'response':response})
							lastMessageTemp["main"] = lastMessage
							lastMessageTemp["response"] = response
							confidence = response.query_result.intent_detection_confidence

			if len(lastMessageTemp) == 0: #no main clause with intent
				for i in range(len(sentences['SUB'])):
					sentencesMain = sentences['SUB'][int(i)]
					i+=1
					for sentence in sentencesMain:
						lastMessage = str(sentence).strip()
						response = df.detect_intent_texts(settings.sessionid, lastMessage)
						if response.query_result.intent.display_name != 'Default Fallback Intent' and response.query_result.intent_detection_confidence > (confidence): #choose better confidence
							#print(lastMessage, response.query_result.intent.display_name, response.query_result.intent_detection_confidence)
							lastMessageTemp["main"] = lastMessage
							lastMessageTemp["response"] = response
							confidence = response.query_result.intent_detection_confidence

			if len(lastMessageTemp)>0:
				return lastMessageTemp
			else:
				return False
		else:
			return False
	except Exception as e:
		play('alert')
		print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
		#master sentence
		return False