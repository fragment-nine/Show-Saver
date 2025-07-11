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

	return
