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

def normalize_header(value):
    return str(value or '').strip().lower()

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
            name_key = None
            tc_key = None
            for row in spamreader:
                if not header:
                    current_header = [str(cell or '').strip() for cell in row]
                    normalized = [normalize_header(cell) for cell in current_header]

                    # Support both old LTC files (NAME/TC) and current TrackMaster exports (Name/TC Stamp).
                    if 'name' in normalized:
                        if 'tc' in normalized:
                            tc_candidate = 'tc'
                        elif 'tc stamp' in normalized:
                            tc_candidate = 'tc stamp'
                        elif 'timecode' in normalized:
                            tc_candidate = 'timecode'
                        else:
                            tc_candidate = None

                        if tc_candidate:
                            header = current_header
                            header_lookup = {normalize_header(col): col for col in current_header}
                            name_key = header_lookup.get('name')
                            tc_key = header_lookup.get(tc_candidate)
                            continue
                    continue

                headers = {}
                for i in range(len(row)):
                    headers[header[i]] = row[i]

                name = headers.get(name_key, '').strip() if name_key else ''
                tc = headers.get(tc_key, '').strip() if tc_key else ''

                if not tc:
                    continue

                # Clean the song name by removing illegal characters.
                name = clean_song_name(name)
                trackMaster.appendRow([tc, name, tools.stampToInt(tc)])

            if not header:
                print('LTC Not Valid')
            print(trackMaster)
    return
