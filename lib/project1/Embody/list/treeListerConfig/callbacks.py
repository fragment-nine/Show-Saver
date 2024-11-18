#Shared Use License: This file is owned by Derivative Inc. (â€œDerivativeï¿½) 
#and can only be used, and/or modified for use, in conjunction with 
#Derivativeâ€™s TouchDesigner software, and only if you are a licensee who 
#has accepted Derivativeâ€™s TouchDesigner license or assignment agreement 
#(which also governs the use of this file).  You may share a modified version 
#of this file with another authorized licensee of Derivativeâ€™s TouchDesigner 
#software.  Otherwise, no redistribution or sharing of this file, with or 
#without modification, is permitted.

"""
All callbacks for this treeLister go here. For available callbacks, see:

https://docs.derivative.ca/Palette:treeLister#Custom_Callbacks

treeLister also has all lister callbacks:
https://docs.derivative.ca/Palette:lister#Custom_Callbacks
"""

# def onInit(info):
# 	info['listerExt'].DefaultRoots = ['/None']

# def getObjectFromID(info):
# 	return {'name': 'TreeObject'}

# def getIDFromObject(info):
# 	return '/None'

# def getObjectChildren(info):
# 	return []

import os

def opPath(info):
	return info['rowData']['Path']

def relFilePath(info):
	return info['rowData']['rel_file_path']

def onClick(info):
	if info['colName'] == 'delete':
		if ui.messageBox('Warning', "Are you sure you want to remove this externalization?\nThis will delete the external file from the file system, \nas well as the operator's externalization tags and external file path.\nThis cannot be undone.", buttons=['No', 'Yes']):
			parent.Embody.RemoveListerRow(opPath(info), relFilePath(info))

	elif info['colName'] == 'Type':
		# open network viewer for this operator
		oper = op(opPath(info))
		x = oper.nodeCenterX
		y = oper.nodeCenterY
		
		for sibling in oper.parent().findChildren(depth=1):
			sibling.selected = False
		oper.selected = True

		pane = ui.panes.createFloating(type=PaneType.NETWORKEDITOR, name=oper.name, maxWidth=1920, maxHeight=1080, monitorSpanWidth=0.9, monitorSpanHeight=0.9)
		pane.owner = oper.parent()
		pane.home(zoom=True, op=oper)
		pane.zoom = 2
		pane.x = x
		pane.y = y

	elif info['colName'] == 'rel_file_path':
		# open file explorer with this file path
		parent.Embody.OpenSaveFile(relFilePath(info))

	elif info['colName'] == 'dirty':
		parent.Embody.Save(opPath(info))
		parent.Embody.Refresh()