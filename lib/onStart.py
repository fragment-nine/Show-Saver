# me - this DAT
# 
# frame - the current frame
# state - True if the timeline is paused
# 
# Make sure the corresponding toggle is enabled in the Execute DAT.

def onStart():
	globals=op('globals')
	op('/SS_UI_v2/UI_Main/left_data/MAIN/1_input_select/input_select/a_select1/dropDownMenu2').par.Value0=globals['a1l',1]
	op('/SS_UI_v2/UI_Main/left_data/MAIN/1_input_select/input_select/a_select1/dropDownMenu3').par.Value0=globals['a1d',1]
	op('/SS_UI_v2/UI_Main/left_data/MAIN/1_input_select/input_select/a_select2/dropDownMenu2').par.Value0=globals['a2l',1]
	op('/SS_UI_v2/UI_Main/left_data/MAIN/1_input_select/input_select/a_select2/dropDownMenu3').par.Value0=globals['a2d',1]
	op('/SS_UI_v2/UI_Main/left_data/MAIN/1_input_select/input_select/a_select3/dropDownMenu2').par.Value0=globals['a3l',1]
	op('/SS_UI_v2/UI_Main/left_data/MAIN/1_input_select/input_select/a_select3/dropDownMenu3').par.Value0=globals['a3d',1]
	op('/SS_UI_v2/UI_Main/left_data/MAIN/1_input_select/input_select/v_select/dropDownMenu').par.Value0=globals['v1l',1]
	op('/SS_UI_v2/UI_Main/left_data/MAIN/1_input_select/input_select/v_select/dropDownMenu1').par.Value0=globals['v1d',1]
	op('/SS_UI_v2/UI_Main/left_data/MAIN/1_input_select/input_select/selectPGM').par.Value0=globals['pgm',1]
	op('/SS_UI_v2/UI_Main/left_data/MAIN/1_input_select/input_select/selectPGMBU').par.Value0=globals['pgmbu',1]
	op('/SS_UI_v2/UI_Main/left_data/MAIN/1_input_select/input_select/selectTC').par.Value0=globals['tc',1]
	op('/SS_UI_v2/UI_Main/left_data/MAIN/1_input_select/input_select/selectTCCompare').par.Value0=globals['tccompare',1]
	op('/SS_UI_v2/UI_Main/left_data/AUDIO/tc_wav/fieldFolderBrowser').par.Value0=globals['wavFolder',1]
	op('/SS_UI_v2/UI_Main/left_data/AUDIO/split_tc_pgm/ltcFolderBrowser').par.Value0=globals['outputFolder',1]
	op('/SS_UI_v2/UI_Main/left_data/AUDIO/split_tc_pgm/pgmFolderBrowser').par.Value0=globals['pgmFolder',1]
	
	return

def onCreate():
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
	return

def onProjectPostSave():
	return

	