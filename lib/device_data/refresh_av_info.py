# me - this DAT
# 
# channel - the Channel object which has changed
# sampleIndex - the index of the changed sample
# val - the numeric value of the changed sample
# prev - the previous sample value
# 
# Make sure the corresponding toggle is enabled in the CHOP Execute DAT.
import text1


def onOffToOn(channel, sampleIndex, val, prev):
	text1.updateLibraryTable()
	text1.updateDeviceTable()
	text1.updateaLibraryTable()
	text1.updateaDeviceTable()
	text1.updateaoLibraryTable()
	text1.updateaoDeviceTable()
	return

def whileOn(channel, sampleIndex, val, prev):
	return

def onOnToOff(channel, sampleIndex, val, prev):
	return

def whileOff(channel, sampleIndex, val, prev):
	return

def onValueChange(channel, sampleIndex, val, prev):
	return
	