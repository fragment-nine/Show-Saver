# me - this DAT
# 
# frame - the current frame
# state - True if the timeline is paused
# 
# Make sure the corresponding toggle is enabled in the Execute DAT.


def onStart():
	return

def onCreate():
	run(f"op('{parent.Embody}').Verify()", delayFrames = 30)

	return

def onExit():
	return

def onFrameStart(frame):
	return

def onFrameEnd(frame):
	return

def onPlayStateChange(state):
	return

def onDeviceChange():
	return

def onProjectPreSave():
	parent.Embody.Update()
	
	return

def onProjectPostSave():
	
	return

	