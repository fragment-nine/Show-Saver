import re

def timecodeToHHMMSS(stamp):
	"""
	Parse timecode from HH:MM:SS, HH:MM:SS:FF, or HH;MM;SS;FF (drop frames).
	Returns HH:MM:SS with zero-padded hours, minutes, and seconds.
	"""
	raw = str(stamp).strip()
	if not raw:
		return ''
	parts = [p for p in re.split(r'[:;]', raw) if p != '']
	if not parts:
		return ''
	if len(parts) >= 4:
		h, m, s, _f = parts[0], parts[1], parts[2], parts[3]
	elif len(parts) == 3:
		h, m, s = parts
	elif len(parts) == 2:
		h, m, s = '0', parts[0], parts[1]
	else:
		h, m, s = '0', '0', parts[0]
	try:
		hi = int(h or 0)
		mi = int(m or 0)
		si = int(s or 0)
	except ValueError:
		return raw
	return f'{hi:02d}:{mi:02d}:{si:02d}'

def stampToInt(stamp):
	#Cast stamp to string in case we get a bad value
	try:
		stamp=str(stamp)
	except:
		print('Couldn\'t cast stamp, may have passed an integer for tc')
		return
	hours,minutes,seconds,frames = 0,0,0,0
	length=len(stamp)
	stamp=stamp.replace(':','')
	frames=stamp[length-2:]
	stamp=stamp[:length-2]
	length=len(stamp)
	seconds=stamp[length-2:]
	stamp=stamp[:length-2]
	length=len(stamp)
	minutes=stamp[length-2:]
	stamp=stamp[:length-2]
	length=len(stamp)
	hours=stamp[length-2:]
	stamp=stamp[:length-2]
	length=len(stamp)
	if hours == '':
		hours=0
	if minutes == '':
		minutes=0
	if seconds == '':
		seconds=0
	if frames == '':
		frames=0
	total=(int(hours)*60*60)+(int(minutes)*60)+(int(seconds))
	return total
