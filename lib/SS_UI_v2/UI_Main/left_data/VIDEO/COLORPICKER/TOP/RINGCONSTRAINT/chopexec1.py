# me - this DAT
# 
# channel - the Channel object which has changed
# sampleIndex - the index of the changed sample
# val - the numeric value of the changed sample
# prev - the previous sample value
# 
# Make sure the corresponding toggle is enabled in the CHOP Execute DAT.

def onOffToOn(channel, sampleIndex, val, prev):
	return

def whileOn(channel, sampleIndex, val, prev):
	return

def onOnToOff(channel, sampleIndex, val, prev):
	return

def whileOff(channel, sampleIndex, val, prev):
	return

def onValueChange(channel, sampleIndex, val, prev):
	
	x = op('math4')[0]
	y = op('math4')[1]
	
	if (x > 0 and y > 0):
		op('constant1').par.value0 = 0
		
	if (x > 0 and y < 0):
		op('constant1').par.value0 = 3
		
	if (x < 0 and y > 0):
		op('constant1').par.value0 = 1
		
	if (x < 0 and y < 0):
		op('constant1').par.value0 = 2
	
	return
	