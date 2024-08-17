# Get Handle to the Operators
audioDevice = op('audiodevin1')
alibraryTable = op('aLibrary')
adeviceTable = op('aDevice')

# Function that handles library changes
def updateaLibraryTable():
    alibraryParam = audioDevice.par.driver
    alibraryTable.clear()

    for label, value in zip(alibraryParam.menuLabels, alibraryParam.menuNames):
        alibraryTable.appendRow([value, label])

# Function that handles device changes
def updateaDeviceTable():
    adeviceParam = audioDevice.par.device
    adeviceTable.clear()

    for label, value in zip(adeviceParam.menuLabels, adeviceParam.menuNames):
        adeviceTable.appendRow([value, label])

# Update the tables initially
updateaLibraryTable()
updateaDeviceTable()