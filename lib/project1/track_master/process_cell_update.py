import tools
import re

# Function to clean the song name by removing illegal characters
def clean_song_name(name):
    # Define a regex pattern that matches illegal characters
    illegal_chars_pattern = r'[\\/:*?"<>|]'

    # Replace any illegal characters with an underscore or another safe character
    cleaned_name = re.sub(illegal_chars_pattern, '_', name)
    return cleaned_name

def onRowChange(dat, rows):
    # Iterate over each changed row
    for rowIndex in rows:
        # Get the first cell (assumed to be the timecode stamp)
        timecode = dat[rowIndex, 0].val  # First column (index 0)

        # Convert the timecode using the tools.stampToInt function
        converted_timecode = tools.stampToInt(timecode)

        # Update the third cell (index 2) with the converted value
        dat[rowIndex, 2] = converted_timecode

        # Get the song name from the second column (index 1)
        song_name = dat[rowIndex, 1].val

        # Clean the song name by removing illegal characters
        cleaned_song_name = clean_song_name(song_name)

        # Update the second column with the cleaned song name
        dat[rowIndex, 1] = cleaned_song_name

    return

def onTableChange(dat):
    return

def onColChange(dat, cols):
    return

def onCellChange(dat, cells, prev):
    return

def onSizeChange(dat):
    return
