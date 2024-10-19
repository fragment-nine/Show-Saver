import datetime

def onValueChange(channel, sampleIndex, val, prev):
    # Button value
    button_value = val  # Current value of the button (0 or 1)

    # The Audio Device Out operator
    audio_device_out = op('/project1/files_out/export_tcwav')
    
    # The DAT holding the full file path (null2)
    name_dat = op('/SS_UI_v2/UI_Main/left_data/AUDIO/tc_wav/null2')

    # Ensure the audio device and DAT exist
    if not audio_device_out or not name_dat:
        print("Error: 'export_tcwav' or 'null2' operator not found.")
        return

    # Fetch the full file path from the DAT
    base_file_path = name_dat[0, 1].val

    # Generate the new file name with timestamp
    current_date = datetime.datetime.now().strftime("%y%m%d")
    file_name = f"ShowSaver_TCWav_Export_v{current_date}.wav"
    full_file_path = f"{base_file_path}/{file_name}"

    # Print the generated file path for debugging purposes
    print(f"Generated file path: {full_file_path}")

    # If button is pressed (value 1), turn on recording and set file path
    if button_value == 1:
        audio_device_out.par.record = 1  # Start recording
        audio_device_out.par.file = full_file_path  # Set the file path for recording
        print(f"Recording started. Output file: {full_file_path}")

    # If button is not pressed (value 0), stop recording
    elif button_value == 0:
        audio_device_out.par.record = 0  # Stop recording
        print("Recording stopped.")

    return
