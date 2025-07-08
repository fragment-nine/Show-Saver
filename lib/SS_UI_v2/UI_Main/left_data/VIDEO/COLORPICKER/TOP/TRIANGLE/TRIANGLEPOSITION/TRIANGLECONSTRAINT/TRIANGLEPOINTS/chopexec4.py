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
	
	point1 = op('null4')[0]
	point2 = op('null4')[1]
	point3 = op('null4')[2]



	if (point1 == 1 and point2 == 0 and point3 == 1):
		
		if (op('parameters')['Ringposition'] > 160 and op('parameters')['Ringposition'] < 200):
			op('constant4').par.value0 = 6
		else :
			op('constant4').par.value0 = 0
	
	elif (point1 == 1 and point2 == 0 and point3 == 0):
		
		if op('parameters')['Ringposition'] < 170:
			op('constant4').par.value0 = 1
		else:
			op('constant4').par.value0 = 7
	
	elif (point1 == 1 and point2 == 1 and point3 == 0):
		if op('parameters')['Ringposition'] < 170:
			op('constant4').par.value0 = 2
		else:
			op('constant4').par.value0 = 8

	elif (point1 == 0 and point2 == 1 and point3 == 0):
		if op('parameters')['Ringposition'] < 170:
			op('constant4').par.value0 = 3
		else:
			op('constant4').par.value0 = 9

	elif (point1 == 0 and point2 == 1 and point3 == 1):
		if op('parameters')['Ringposition'] < 170:
			op('constant4').par.value0 = 4
		else:
			op('constant4').par.value0 = 10

	elif (point1 == 0 and point2 == 0 and point3 == 1):
		if op('parameters')['Ringposition'] < 170:
			op('constant4').par.value0 = 5
		else:
			op('constant4').par.value0 = 11


	return
	