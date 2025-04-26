# me - this DAT
#
# channel       - the Channel object which has changed
# sampleIndex   - the index of the changed sample
# val           - the numeric value of the changed sample
# prev          - the previous sample value
#
# Make sure the corresponding toggle is enabled in the CHOP Execute DAT.

import startLTC

def onOffToOn(channel, sampleIndex, val, prev):
    pass

def whileOn(channel, sampleIndex, val, prev):
    pass

def onOnToOff(channel, sampleIndex, val, prev):
    pass

def whileOff(channel, sampleIndex, val, prev):
    pass

def start():
    op('timer1').par.start.pulse()
    op('timer2').par.start.pulse()

def stop():
    op('timer1').par.initialize.pulse()
    op('timer2').par.initialize.pulse()

def onValueChange(channel, sampleIndex, val, prev):
    # Table DAT tracking [0]=last time, [1]=change‐flag
    tbl = op('currentLTC')

    # If flag was set, clear it, trigger startLTC callback and restart timers
    try:
        flag = int(tbl[1,0].val)
    except:
        flag = 0
    if flag == 1:
        tbl[1,0].val = '0'
        try:
            startLTC.onValueChange(channel, sampleIndex, val, prev)
        except Exception as e:
            debug('startLTC callback error:', e)
        start()

    # Read the new timecode (in seconds)
    try:
        current = op('ltcin1')['total_seconds'][0]
    except Exception as e:
        debug('Error reading LTC timecode:', e)
        return

    # Read the old timecode (or default to current)
    try:
        old = float(tbl[0,0].val)
    except:
        old = current

    # Let startLTC do its own housekeeping every time
    try:
        startLTC.onValueChange(channel, sampleIndex, val, prev)
    except:
        pass

    # Pull song names from your track_master NAME DAT
    nameDAT = op('../track_master/name')
    try:
        new_song      = nameDAT[1,0].val
    except:
        new_song = ''
    try:
        previous_song = nameDAT[3,0].val
    except:
        previous_song = ''

    # Decide whether to restart or continue
    if abs(current - old) > 240:
        stop()
        tbl[1,0].val = '1'
        print('Timecode has changed')
    elif new_song != previous_song:
        stop()
        tbl[1,0].val = '1'
        print('Song has changed')
    else:
        start()

    # Store the new state
    tbl[0,0].val = str(current)
    nameDAT[3,0].val = new_song

    return