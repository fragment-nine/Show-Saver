# me - this DAT
# 
# channel - the Channel object which has changed
# sampleIndex - the index of the changed sample
# val - the numeric value of the changed sample
# prev - the previous sample value
# 
# Make sure the corresponding toggle is enabled in the CHOP Execute DAT.

def onOffToOn(channel, sampleIndex, val, prev):
	
	op('switch2').par.index = 0
	op('switch4').par.index = 0
	
	return

def whileOn(channel, sampleIndex, val, prev):
	return

def onOnToOff(channel, sampleIndex, val, prev):
	
	op('constant1').par.value0.val = op('OUT2')[0]
	op('constant1').par.value1.val = op('OUT2')[1]
	
	op('constant2').par.value0.val = op('parameters')['Ringposition']
	
	return

def whileOff(channel, sampleIndex, val, prev):
	return

def onValueChange(channel, sampleIndex, val, prev):
	return
	