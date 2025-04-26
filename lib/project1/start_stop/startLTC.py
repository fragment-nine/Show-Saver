# me – this DAT (startLTC)

import os
import tools

def makeFolders(date):
    # Your three base-folder Table DATs:
    pgmDAT = op('/SS_UI_v2/UI_Main/left_data/SETTINGS/split_tc_pgm/null2')
    ltcDAT = op('/SS_UI_v2/UI_Main/left_data/SETTINGS/split_tc_pgm/null6')
    wavDAT = op('/SS_UI_v2/UI_Main/left_data/SETTINGS/split_tc_pgm/null4')

    bases = []
    for name, dat in (('pgmFolder', pgmDAT),
                      ('ltcFolder', ltcDAT),
                      ('wavFolder', wavDAT)):
        if not dat:
            debug(f"makeFolders: DAT for {name} not found at expected path")
            continue
        try:
            basePath = dat[0,1].val
        except Exception as e:
            debug(f"makeFolders: error reading {name}[0,1]:", e)
            continue
        if not basePath:
            debug(f"makeFolders: {name} path is empty")
            continue
        bases.append(basePath)

    if not bases:
        debug("makeFolders: no valid base paths found, aborting")
        return

    # Create Day folder and Long Recordings subfolder
    for base in bases:
        dayFolder  = os.path.join(base, date)
        longFolder = os.path.join(base, 'Long Recordings', date)
        for p in (dayFolder, longFolder):
            if not os.path.exists(p):
                try:
                    os.makedirs(p)
                    print(f"Created directory: {p}")
                except Exception as e:
                    debug(f"makeFolders: failed to create {p}:", e)

def getDate():
    c = op('clock')
    return f"{int(c['year'][0]):02d}{int(c['month'][0]):02d}{int(c['day'][0]):02d}"

def getTime():
    c = op('clock')
    return f"{int(c['hour'][0]):02d}{int(c['min'][0]):02d}{int(c['sec'][0]):02d}"

def onValueChange(channel, sampleIndex, val, prev):
    trackMaster = op('/project1/track_master/trackMaster')
    nameTable   = op('/project1/track_master/name')
    ltcCHOP     = op('ltcin1')

    date = getDate()
    time = getTime()

    # Read timecode safely
    try:
        ltcTotal = float(ltcCHOP['total_seconds'][0])
    except Exception as e:
        debug("onValueChange: couldn't read total_seconds:", e)
        return

    # Determine song
    song = ''
    for i in range(trackMaster.numRows):
        try:
            thresh = int(trackMaster[i,2].val)
        except:
            continue
        if ltcTotal < thresh:
            song = trackMaster[i-1,1].val.replace('/','')
            break

    makeFolders(date)

    # Write out into your name table
    nameTable[0,0].val = f"{date}/{song}_{date}_{time}"
    nameTable[1,0].val = song
    nameTable[2,0].val = f"{date}_{time}"
    return

def manualStart(channel=None, sampleIndex=None, val=None, prev=None):
    nameTable = op('/project1/track_master/name')
    date = getDate()
    time = getTime()
    song = "Manual Start"

    makeFolders(date)

    nameTable[0,0].val = f"{date}/{song}_{date}_{time}"
    nameTable[1,0].val = song
    nameTable[2,0].val = f"{date}_{time}"
    return