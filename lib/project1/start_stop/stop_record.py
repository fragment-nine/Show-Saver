# me - this DAT
#
# channel - the Channel object which has changed
# sampleIndex - the index of the sample that changed
# val - the numeric value of the sample
# prev - the previous sample value
#
# Target: `pgm` CHOP in /project1/start_stop (timer output: ~0 = inactive, ~1 = active).
# Enable Value Change on this CHOP Execute. Crossing from active to inactive sends the
# same OSC stop path as LTC idle (notify_program_stop).

import time
import trigExecute

_LAST_PGM_STOP_TIME = 0.0
_PGM_DEBOUNCE_SEC = 0.05


def _maybe_pgm_stop(reason):
	global _LAST_PGM_STOP_TIME
	now = time.time()
	if now - _LAST_PGM_STOP_TIME < _PGM_DEBOUNCE_SEC:
		return
	_LAST_PGM_STOP_TIME = now
	trigExecute.notify_program_stop(reason)


def onOffToOn(channel, sampleIndex, val, prev):
	return


def whileOn(channel, sampleIndex, val, prev):
	return


def onOnToOff(channel, sampleIndex, val, prev):
	# Fires when channel crosses from "on" to "off" (non-zero → 0). Enable if you use sharp 0/1 only.
	_maybe_pgm_stop('pgm CHOP on→off')


def whileOff(channel, sampleIndex, val, prev):
	return


def onValueChange(channel, sampleIndex, val, prev):
	# Handles ramps: inactive = below 0.5, active = 0.5 and up.
	try:
		v = float(val)
		p = float(prev)
	except (TypeError, ValueError):
		return
	if p >= 0.5 and v < 0.5:
		_maybe_pgm_stop('pgm output inactive (timer / active channel)')
	return
