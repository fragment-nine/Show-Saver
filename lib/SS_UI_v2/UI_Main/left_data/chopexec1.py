# me - this DAT
# 
# channel - the Channel object which has changed
# sampleIndex - the index of the changed sample
# val - the numeric value of the changed sample
# prev - the previous sample value
# 
# Make sure the corresponding toggle is enabled in the CHOP Execute DAT.

def onValueChange(channel, sampleIndex, val, prev):
    op('viewer').par.selectpanel = 'MAIN' if val == 0 else (
        'AUDIO' if val == 1 else (
        'LAYOUT' if val == 2 else (
        'FILE' if val == 3 else 'DEFAULT')))
    return

	