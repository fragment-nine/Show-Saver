import csv
import tools
import re

print('LTC')

# Function to clean the song name by removing illegal characters
def clean_song_name(name):
    # Define a regex pattern that matches illegal characters
    illegal_chars_pattern = r'[\\/:*?"<>|]'
    
    # Replace any illegal characters with an underscore or another safe character
    cleaned_name = re.sub(illegal_chars_pattern, '_', name)
    return cleaned_name

def onOffToOn(channel, sampleIndex, val, prev):
    print('Resetting LTC File')
    file = op('constants')['ltcLocation', 1]
    print(file)
    trackMaster = op('trackMasterRaw')
    if file:
        print('File has a value')
        trackMaster.clear()
        with open(str(file), newline='') as csvfile:
            # Read a sample to detect the delimiter
            sample = csvfile.read(1024)
            csvfile.seek(0)  # Reset file pointer to beginning
            
            # Detect the delimiter
            sniffer = csv.Sniffer()
            delimiter = sniffer.sniff(sample).delimiter
            print(f'Detected delimiter: "{delimiter}"')
            
            spamreader = csv.reader(csvfile, delimiter=delimiter)
            header = None
            for row in spamreader:
                if header:
                    headers = {}
                    for i in range(len(row)):
                        headers[header[i]] = row[i]
                    
                    name, tc = '', ''
                    if 'NAME' in headers:
                        name = headers['NAME']
                        # Clean the song name by removing illegal characters
                        name = clean_song_name(name)
                    if 'TC' in headers:
                        tc = headers['TC']
                    
                    trackMaster.appendRow([tc, name, tools.stampToInt(tc)])
                else:
                    header = []
                    for i in range(len(row)):
                        header.append(row[i])
                    valid = True
                    if 'NAME' not in header:
                        valid = False
                    if 'TC' not in header:
                        valid = False
                    if not valid:
                        print('LTC Not Valid')
                        break
            print(trackMaster)
    return
