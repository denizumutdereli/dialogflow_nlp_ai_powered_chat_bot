import os
import sys
import winsound
import settings

def play(appType):
	if settings.alertSounds == 1:
		if appType == 'opening':
			winsound.PlaySound(settings.workingPath + "\\sounds\\opening.wav", winsound.SND_FILENAME)
		elif appType == 'sent':
			winsound.PlaySound(settings.workingPath + "\\sounds\\sent.wav", winsound.SND_FILENAME)
		elif appType == 'alert':
			winsound.PlaySound(settings.workingPath + "\\sounds\\alert.wav", winsound.SND_FILENAME)
		else:
			winsound.PlaySound(settings.workingPath + "\\sounds\\info.wav", winsound.SND_FILENAME)