# me - this DAT
# 
# channel - the Channel object which has changed
# sampleIndex - the index of the changed sample
# val - the numeric value of the changed sample
# prev - the previous sample value
# 
# Make sure the corresponding toggle is enabled in the CHOP Execute DAT.

def onOffToOn(channel, sampleIndex, val, prev):
	op('/project1/start_stop/timer1').par.initialize.pulse()
	op('/project1/start_stop/timer2').par.initialize.pulse()
	op('/project1/start_stop/timer3').par.initialize.pulse()
	op('/project1/start_stop/timer4').par.initialize.pulse()
	return

def whileOn(channel, sampleIndex, val, prev):
	return

def onOnToOff(channel, sampleIndex, val, prev):
	return

def whileOff(channel, sampleIndex, val, prev):
	return

def onValueChange(channel, sampleIndex, val, prev):
	return
	