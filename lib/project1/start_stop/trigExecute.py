# me - this DAT
#
# channel - the Channel object which has changed
# sampleIndex - the index of the changed sample
# val - the numeric value of the changed sample
# prev - the previous sample value
#
# Make sure the corresponding toggle is enabled in the CHOP Execute DAT.
#
# Idle stop: enable "While On" on this CHOP Execute (same target as Value Change,
# e.g. ltcin1). While total_seconds stays unchanged for LTC_IDLE_TIMEOUT_SEC wall
# seconds, we send OSC stop and reset timers. If your TC sits at 0 when idle and
# While On does not run, point a second CHOP Execute at a constant CHOP and call
# tick_ltc_idle_watch() from its While On.

import time
import startLTC

current_song = ''
_last_final_running = None

LTC_IDLE_TIMEOUT_SEC = 15.0
_LTC_IDLE_EPS = 1e-5
_ltc_idle_last_sec = None
_ltc_idle_last_change = None
_ltc_idle_stop_sent = False

def _touch_ltc_activity(sec):
	"""Reset idle timer — call when we know LTC advanced or CHOP reported a change."""
	global _ltc_idle_last_sec, _ltc_idle_last_change, _ltc_idle_stop_sent
	_ltc_idle_last_sec = float(sec)
	_ltc_idle_last_change = time.time()
	_ltc_idle_stop_sent = False

def tick_ltc_idle_watch():
	"""Call from While On every frame (or from a always-cooking CHOP)."""
	global _ltc_idle_last_sec, _ltc_idle_last_change, _ltc_idle_stop_sent
	try:
		ltc = op('ltcin1')
		cur = float(ltc['total_seconds'])
	except Exception:
		return
	now = time.time()
	if _ltc_idle_last_sec is None:
		_ltc_idle_last_sec = cur
		_ltc_idle_last_change = now
		return
	if abs(cur - _ltc_idle_last_sec) > _LTC_IDLE_EPS:
		if _ltc_idle_stop_sent:
			print('[LTC/trig] idle: timecode advancing again after idle stop')
		_ltc_idle_last_sec = cur
		_ltc_idle_last_change = now
		_ltc_idle_stop_sent = False
		return
	if now - _ltc_idle_last_change < LTC_IDLE_TIMEOUT_SEC:
		return
	if _ltc_idle_stop_sent:
		return
	_ltc_idle_stop_sent = True
	notify_program_stop(f'idle timeout ({LTC_IDLE_TIMEOUT_SEC}s) — frozen ltcin1 total_seconds')

def onOffToOn(channel, sampleIndex, val, prev):
	return

def whileOn(channel, sampleIndex, val, prev):
	tick_ltc_idle_watch()
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

def notify_program_stop(reason='external'):
	"""Timers init, resume flag set, OSC stop — shared by idle timeout, pgm `stop_record`, etc."""
	global _last_final_running
	stop()
	try:
		op('currentLTC')[1, 0] = 1
	except Exception:
		pass
	_last_final_running = False
	startLTC.push_song_osc(False, force=True)
	if reason:
		print(f'[LTC/trig] program stop — {reason}')

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
	# force=True when stopping so OSC is not skipped if payload matches last send
	startLTC.push_song_osc(final_running, force=(not final_running))
	_touch_ltc_activity(current)
	return
