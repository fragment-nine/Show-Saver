# me - this DAT
#
# channel - the Channel object which has changed
# sampleIndex - the index of the changed sample
# val - the numeric value of the changed sample
# prev - the previous sample value
#
# Make sure the corresponding toggle is enabled in the CHOP Execute DAT.
import os
import tools

_last_song_osc_key = None

def push_song_osc(running):
	"""
	Send current song + wall-clock timestamp on oscout1 (OSC Out DAT).
	One OSC message /showsaver/ltc with args: combined string (song\\tdate_time), run state (1/0).
	Skips duplicate consecutive payloads (LTC can tick faster than wall-clock text changes).
	"""
	global _last_song_osc_key
	o = op('oscout1')
	if o is None or not hasattr(o, 'sendOSC'):
		print('[LTC/OSC] oscout1 missing or not an OSC Out DAT (no sendOSC); not sending')
		return
	nm = op('../track_master/name')
	song = str(nm[1, 0]) if nm.numRows > 1 else ''
	ts = str(nm[2, 0]) if nm.numRows > 2 else ''
	combined = f'{song}\t{ts}'
	run_f = 1.0 if running else 0.0
	key = (combined, run_f)
	if key == _last_song_osc_key:
		return
	_last_song_osc_key = key
	try:
		# TD API: sendOSC(addr, list_of_args) — pairs (addr, list) for multiple messages.
		nbytes = o.sendOSC('/showsaver/ltc', [combined, run_f])
		print(f'[LTC/OSC] sendOSC /showsaver/ltc  song+ts={combined!r}  run={run_f}  bytes={nbytes}')
	except Exception as e:
		print(f'[LTC/OSC] sendOSC failed: {e!r}')

def makeFolders(date):
    # Pull each global individually
    outputFolder = str(op('/SS_UI_v2/UI_Main/left_data/SETTINGS/split_tc_pgm/null6')[0, 1])
    pgmFolder = str(op('/SS_UI_v2/UI_Main/left_data/SETTINGS/split_tc_pgm/null2')[0, 1])
    wavFolder = str(op('/SS_UI_v2/UI_Main/left_data/SETTINGS/split_tc_pgm/null4')[0, 1])
    
    # Define a list of folders to process
    folderPaths = [outputFolder, pgmFolder, wavFolder]
    
    # Loop through each folder path and create directories
    for basePath in folderPaths:
        path = basePath + '/' + date
        longPath = basePath + '/Long Recordings/' + date

        # Create the main folder if it doesn't exist
        if not os.path.exists(path):
            os.makedirs(path)
            print(f"The new directory is created: {path}")
        
        # Create the 'Long Recordings' folder if it doesn't exist
        if not os.path.exists(longPath):
            os.makedirs(longPath)
            print(f"The new directory is created: {longPath}")
    
    return

def getDate():
	date=str('{0:02d}'.format(int(op('clock')['year'])))+str('{0:02d}'.format(int(op('clock')['month'])))+str('{0:02d}'.format(int(op('clock')['day'])))
	return date

def getTime():
	time=str('{0:02d}'.format(int(op('clock')['hour'])))+str('{0:02d}'.format(int(op('clock')['min'])))+str('{0:02d}'.format(int(op('clock')['sec'])))
	return time

def onValueChange(channel, sampleIndex, val, prev):
	trackMaster=op('/project1/track_master/trackMaster')
	name=op('../track_master/name')
	ltc=op('ltcin1')

	date=getDate()
	time=getTime()

	ltcTotal=ltc['total_seconds']
	song=''
	
	for i in range(trackMaster.numRows):
		if  ltcTotal < int(trackMaster[i,2]):
			song = str(trackMaster[i-1,1]).replace('/','')
			break

	makeFolders(date)

	name[0,0]=date+r'/'+song+'_'+date+'_'+time
	name[1,0]=song
	name[2,0]=date+'_'+time

	return

def manualStart():
	trackMaster=op('/project1/track_master/trackMaster')
	name=op('../track_master/name')
	ltc=op('ltcin1')

	date=getDate()
	time=getTime()

	song="Manual Start"

	makeFolders(date)

	name[0,0]=date+r'/'+song+'_'+date+'_'+time
	name[1,0]=song
	name[2,0]=date+'_'+time

	push_song_osc(True)

	return
