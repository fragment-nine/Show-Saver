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
