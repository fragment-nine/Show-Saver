# me - this DAT
#
# channel - the Channel object which has changed
# sampleIndex - the index of the changed sample
# val - the numeric value of the changed sample
# prev - the previous sample value
#
# Make sure the corresponding toggle is enabled in the CHOP Execute DAT.
import startLTC
import os
def onOffToOn(channel, sampleIndex, val, prev):
	date=startLTC.getDate()
	time=startLTC.getTime()
	name=op('name')
	startLTC.makeFolders(date)
	track=parent.Project.par.Nonltctrackname
	name[0,0]=date+r'/'+ track +'_'+date+'_'+time
	name[1,0]=track
	name[2,0]=date+'_'+time
	print('Started Manually')
	return

def whileOn(channel, sampleIndex, val, prev):
	return

def onOnToOff(channel, sampleIndex, val, prev):
	return

def whileOff(channel, sampleIndex, val, prev):
	return

def onValueChange(channel, sampleIndex, val, prev):
	return
