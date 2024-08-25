ShowSaver

ShowSaver is a custom TouchDesigner project that is designed to record live entertainment rehearsals and performances driven by LTC timecode. Files are broken up per song with various audio routing options to generate the exact files you need. These files use compressed codecs to allow for small file sizes and instand uploads to Dropbox, Drive, FTP, etc. so that all the songs are instantly viewable after the rehearsal.

Features
-Start/Stop/Advance recordings based on LTC timecode on any audio device connected to your computer
-Produce a single file for each song/section of timecode
-Produce a long recording that starts either manually or when timecode rolls to record the entire rehearsal
-Embed audio that is either timecode on the left channel and program audio on the right channel for programmer playback later
-Embed program audio on both channels so you don't blow your ear drumes out playing back the file or sharing it externally
-Burn in the timecode stamp, date/time stamp, and track name into the recording
-Short files are labeled with the song name and start time for easy recall
-Monitor current timecode and program audio in the UI
-Timecode and program audio can come in on the same or seperate audio devices


Getting Started
1. Select your audio and video devices, you may select up to 3 audio devices but only 1 is required. Make sure you select the library first
2. Fill in the Track Master with the timecode start points for all your sections. (Make sure the start point is BEFORE the first frame of timecode that will hit. If pre-roll happens 2 seconds before the hour mark, make sure it is at least one frame before the first received frame)
3. Set the record folder or your files will go nowhere

About TouchDesigner
TouchDesigner is a fantastic development platform if you're not familiar with it. No knowledge or expertise is required to use ShowSaver. You do however need to download and install TouchDesigner to be able to run ShowSaver. TouchDesigner is free for non-commercial use and ShowSaver is fully functional with the non-commercial version, resolution is just capped at 720p. Once you're using this in a commercial setting, you're required to purchase a commercial license per the EULA for TouchDesigner. This can be either a TouchPlayer or TouchDesigner Commercial License ($300 and $600 respectively). This version was built with TouchDesigner 2023.11760 and should run on this or any later version. It has been tested on Mac and PC. You can download TouchDesigner here: https://derivative.ca/download
