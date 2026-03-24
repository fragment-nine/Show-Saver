# me - this DAT
#
# channel - the Channel object which has changed
# sampleIndex - the index of the changed sample
# val - the numeric value of the changed sample
# prev - the previous sample value
#
# Make sure the corresponding toggle is enabled in the CHOP Execute DAT.

import startLTC
current_song=""
_last_final_running = None

def onOffToOn(channel, sampleIndex, val, prev):
	return

def whileOn(channel, sampleIndex, val, prev):
	return

def onOnToOff(channel, sampleIndex, val, prev):
	return

def whileOff(channel, sampleIndex, val, prev):
	return

def start():
	op('timer1').par.start.pulse()
	op('timer2').par.start.pulse()

def stop():
	op('timer1').par.initialize.pulse()
	op('timer2').par.initialize.pulse()

def onValueChange(channel, sampleIndex, val, prev):
	global _last_final_running
	if op('currentLTC')[1,0]==1:
		op('currentLTC')[1,0]=0
		startLTC.onValueChange(1,1,1,1)
		start()
		print('[LTC/trig] resume after stop flag: pulsed timers + refreshed name from LTC')
	current=op('ltcin1')['total_seconds']
	old=op('currentLTC')[0,0]

	# Check if the song has changed
	startLTC.onValueChange(1,1,1,1)
	new_song=op('../track_master/name')[1,0]
	current_song=op('../track_master/name')[3,0]
	#print(f"Current song: {current_song} New song: {new_song}")

	final_running = True
	if current+240 < old or current -240 > old:
		stop()
		#startLTC.onValueChange(1,1,1,1)
		op('currentLTC')[1,0]=1
		final_running = False
		print(f'[LTC/trig] timecode jump  ltc_s={current}  prev_stored_s={old}  song={new_song!r}  (was {current_song!r})')
	elif new_song!=current_song:
		stop()
		#startLTC.onValueChange(1,1,1,1)
		op('currentLTC')[1,0]=1
		final_running = False
		print(f'[LTC/trig] song change  ltc_s={current}  {current_song!r} -> {new_song!r}')
	else:
		#startLTC.onValueChange(1,1,1,1)
		start()
	op('currentLTC')[0,0]=current
	# Update the current song
	op('../track_master/name')[3,0]=new_song
	if final_running != _last_final_running:
		print(f'[LTC/trig] running state {_last_final_running} -> {final_running}  ltc_s={current}  song={new_song!r}')
		_last_final_running = final_running
	startLTC.push_song_osc(final_running)
	return
