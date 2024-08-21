# me - this DAT
# 
# channel - the Channel object which has changed
# sampleIndex - the index of the changed sample
# val - the numeric value of the changed sample
# prev - the previous sample value
# 
# Make sure the corresponding toggle is enabled in the CHOP Execute DAT.

def offToOn(channel, sampleIndex, val, prev):
    print("Window on top = TRUE")
    op('/perform').par.alwaysontop = 1
    return

def whileOn(channel, sampleIndex, val, prev):
    return

def onToOff(channel, sampleIndex, val, prev):
    print("Window on top = FALSE")
    op('/perform').par.alwaysontop = 0
    return

def whileOff(channel, sampleIndex, val, prev):
	return

def onValueChange(channel, sampleIndex, val, prev):
	return
	