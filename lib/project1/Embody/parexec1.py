# me - this DAT
# par - the Par object that has changed
# val - the current value
# prev - the previous value
# 
# Make sure the corresponding toggle is enabled in the Parameter Execute DAT.

import webbrowser

def onValueChange(par, prev):
	# use par.eval() to get current value
	if par.name == 'Folder':
		parent.Embody.Disable(prev, removeTags=False)
		run(f"op('{parent.Embody}').UpdateHandler()", delayFrames = 60)

	elif par.name == 'Externalizations':
		if not par:
			parent.Embody.MissingExternalizationsPar()
		
	return

def onPulse(par):
	if par.name == 'Disable':
		parent.Embody.DisableHandler()
		
	elif par.name == 'Update':
		parent.Embody.UpdateHandler()

	elif par.name == 'Refresh':
		parent.Embody.Refresh()

	elif par.name == 'Openmanager':
		parent.Embody.Manager('open')

	elif par.name == 'Closemanager':
		parent.Embody.Manager('close')
				
	elif par.name == 'Github':
		webbrowser.open('https://github.com/dylanroscover/Embody')

	elif par.name == 'Help':
		op('help').openViewer()

	elif par.name == 'Openexternalizationstable':
		parent.Embody.OpenTable()

	elif par.name == 'Externalizeproject':
		parent.Embody.ExternalizeProject()
	
	return

def onExpressionChange(par, val, prev):
	return

def onExportChange(par, val, prev):
	return

def onEnableChange(par, val, prev):
	return

def onModeChange(par, val, prev):
	return
	