# me - this DAT
# 
# channel - the Channel object which has changed
# sampleIndex - the index of the changed sample
# val - the numeric value of the changed sample
# prev - the previous sample value
# 
# Make sure the corresponding toggle is enabled in the CHOP Execute DAT.



def onValueChange(channel, sampleIndex, val, prev):
	op('/project1/start_stop/timer1').par.start.pulse()
	op('/project1/start_stop/timer2').par.start.pulse()
	op('/project1/start_stop/timer3').par.start.pulse()
	op('/project1/start_stop/timer4').par.start.pulse()
	op('/project1/start_stop/manualStart').par.const0value=1
	return
	
	