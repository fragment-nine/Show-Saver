# me - this DAT
#
# channel - the Channel object which has changed
# sampleIndex - the index of the changed sample
# val - the numeric value of the changed sample
# prev - the previous sample value
#
# Make sure the corresponding toggle is enabled in the CHOP Execute DAT.

import startLTC

def onOffToOn(channel, sampleIndex, val, prev):
	return

def whileOn(channel, sampleIndex, val, prev):
	return

def onOnToOff(channel, sampleIndex, val, prev):
	return

def whileOff(channel, sampleIndex, val, prev):
	return

def start():
	op('timer1').par.start.pulse()
	op('timer2').par.start.pulse()

def stop():
	op('timer1').par.initialize.pulse()
	op('timer2').par.initialize.pulse()

def onValueChange(channel, sampleIndex, val, prev):
	if op('currentLTC')[1,0]==1:
		op('currentLTC')[1,0]=0
		startLTC.onValueChange(1,1,1,1)
		start()
	current=op('ltcin1')['total_seconds']
	old=op('currentLTC')[0,0]
	if current+240 < old or current -240 > old:
		stop()
		startLTC.onValueChange(1,1,1,1)
		op('currentLTC')[1,0]=1
	else:
		startLTC.onValueChange(1,1,1,1)
		start()
	op('currentLTC')[0,0]=current
	return
