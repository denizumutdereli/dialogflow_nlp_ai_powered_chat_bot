from documentRetrievalModel import documentRetrievalModel as DRM
from processedQuestion import processedQuestion as PQ
from pathlib import Path
import codecs
import re
import sys
import settings
import tl

#datasetName = settings.workingPath + '/nlp/semisupervised.txt'

def train(sentence,account):
	personaFile = Path(settings.workingPath + "/nlp/"+str(account)+'_semisupervised.log')
	if personaFile.is_file():
		with codecs.open(personaFile, encoding='utf-8') as fobj:
			text = fobj.read()
	else:
		with codecs.open(personaFile, mode='a',  encoding='utf-8'): pass

	with codecs.open(personaFile, 'a', encoding='utf-8') as fobj:
		if not sentence.endswith('\n'):
			fobj.write('\n')
		fobj.write(sentence)
	fobj.close()


def askQuestion(question,account = '',supervised=False):
	try:
		#print('ai')
		if supervised == False:
			#print('super')
			datasetFile = settings.workingPath + '/nlp/'+str(account)+'_semisupervised.log'
		else:
			#print('non super')
			datasetFile = settings.workingPath + '/nlp/supervised.log'
		if settings.personaFile == '':	
			dataset = open(datasetFile,"r", encoding= 'unicode_escape')
		else:
			dataset = settings.personaFile
	except FileNotFoundError:
		print("Bot> Oops! I am unable to locate \"" + datasetFile + "\"")
		return False

	paragraphs = []
	for para in dataset.readlines():
		if(len(para.strip()) > 0):
			paragraphs.append(para.strip())

	# Processing Paragraphs
	drm = DRM(paragraphs,True,True)

	# Proocess Question
	pq = PQ(question,True,False,True)
	# Get Response From Trained Data
	response =drm.query(pq)

	if len(response)<5:
		#print(response)
		return False
	else:
		#print(response)
		#print(tl.translate(response, settings.translateDestination))
		#print()
		return response
"""
while True:
	q = input('question:')
	askQuestion(tl.translate(q, 'de'),1,True)"""

#train('translation test with supervise!',1)