# me - this DAT
#
# channel - the Channel object which has changed
# sampleIndex - the index of the changed sample
# val - the numeric value of the changed sample
# prev - the previous sample value
#
# Make sure the corresponding toggle is enabled in the CHOP Execute DAT.
import csv
import tools

print('LTC')

def onOffToOn(channel, sampleIndex, val, prev):
	print('Resetting LTC File')
	file=op('constants')['ltcLocation',1]
	print(file)
	trackMaster=op('trackMasterRaw')
	if file:
		print('File has a value')
		trackMaster.clear()
		with open(str(file), newline='') as csvfile:
			spamreader = csv.reader(csvfile,delimiter=',',)
			header=None
			for row in spamreader:
				if header:
					headers={}
					for i in range(len(row)):
						headers[header[i]]=row[i]
					name,tc = '',''
					if 'NAME' in headers:
						name = headers['NAME']
					if 'TC' in headers:
						tc = headers['TC']
					trackMaster.appendRow([tc,name,tools.stampToInt(tc)])
				else:
					header=[]
					for i in range(len(row)):
						header.append(row[i])
					valid=True
					if 'NAME' not in header:
						valid = False
					if 'TC' not in header:
						valid = False
					if not valid:
						print('LTC Not Valid')
						break
			print(trackMaster)
	return
