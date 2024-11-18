# me - this DAT
# 
# channel - the Channel object which has changed
# sampleIndex - the index of the changed sample
# val - the numeric value of the changed sample
# prev - the previous sample value
# 
# Make sure the corresponding toggle is enabled in the CHOP Execute DAT.

def onOffToOn(channel, sampleIndex, val, prev):
	return

def whileOn(channel, sampleIndex, val, prev):
	return

def onOnToOff(channel, sampleIndex, val, prev):
	return

def whileOff(channel, sampleIndex, val, prev):
	return

import subprocess
import os
import time

def valueChange(channel, sampleIndex, val, prev):
    if val == 1:  # Trigger on button press
        project_path = "C:/Users/andre/OneDrive/Documents/GitHub/Show-Saver/ShowSaver.toe"
        touchdesigner_path = "C:/Program Files/Derivative/TouchDesigner/bin/TouchDesigner.exe"

        print("Saving project...")
        project.save()

        command = f'"{touchdesigner_path}" "{project_path}"'
        print(f"Opening new instance of project: {project_path}")

        try:
            process = subprocess.Popen(command, shell=True)
            print(f"Process started with PID: {process.pid}")
        except Exception as e:
            print(f"Error opening new project instance: {e}")

        # Give some time for the new instance to start
        time.sleep(2)

        # Close the current instance of TouchDesigner
        project.quit()

    return
