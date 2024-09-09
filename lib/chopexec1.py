# me - this DAT
# 
# channel - the Channel object which has changed
# sampleIndex - the index of the changed sample
# val - the numeric value of the changed sample
# prev - the previous sample value
# 
# Make sure the corresponding toggle is enabled in the CHOP Execute DAT.

def onOffToOn(channel, sampleIndex, val, prev):
	globals=op('globals')
	op('/SS_UI_v2/UI_Main/left_data/1_input_select/input_select/a_select1/dropDownMenu2').par.Value0=globals['a1l',1]
	op('/SS_UI_v2/UI_Main/left_data/1_input_select/input_select/a_select1/dropDownMenu3').par.Value0=globals['a1d',1]
	op('/SS_UI_v2/UI_Main/left_data/1_input_select/input_select/a_select2/dropDownMenu2').par.Value0=globals['a2l',1]
	op('/SS_UI_v2/UI_Main/left_data/1_input_select/input_select/a_select2/dropDownMenu3').par.Value0=globals['a2d',1]
	op('/SS_UI_v2/UI_Main/left_data/1_input_select/input_select/a_select3/dropDownMenu2').par.Value0=globals['a3l',1]
	op('/SS_UI_v2/UI_Main/left_data/1_input_select/input_select/a_select3/dropDownMenu3').par.Value0=globals['a3d',1]
	op('/SS_UI_v2/UI_Main/left_data/1_input_select/input_select/v_select/dropDownMenu').par.Value0=globals['v1l',1]
	op('/SS_UI_v2/UI_Main/left_data/1_input_select/input_select/v_select/dropDownMenu1').par.Value0=globals['v1d',1]
	op('/SS_UI_v2/UI_Main/left_data/1_input_select/input_select/selectPGM').par.Value0=globals['pgm',1]
	op('/SS_UI_v2/UI_Main/left_data/1_input_select/input_select/selectPGMBU').par.Value0=globals['pgmbu',1]
	op('/SS_UI_v2/UI_Main/left_data/1_input_select/input_select/selectTC').par.Value0=globals['tc',1]
	op('/SS_UI_v2/UI_Main/left_data/1_input_select/input_select/selectTCCompare').par.Value0=globals['tccompare',1]
	return

def whileOn(channel, sampleIndex, val, prev):
	return

def onOnToOff(channel, sampleIndex, val, prev):
	return

def whileOff(channel, sampleIndex, val, prev):
	return

def onValueChange(channel, sampleIndex, val, prev):
	return
	