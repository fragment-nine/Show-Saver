# Get Handle to the Operators
videoDevice = op('videodevin1')
libraryTable = op('vLibrary')
deviceTable = op('vDevice')

# Function that handles library changes
def updateLibraryTable():
    libraryParam = videoDevice.par.library
    libraryTable.clear()

    for label, value in zip(libraryParam.menuLabels, libraryParam.menuNames):
        libraryTable.appendRow([value, label])
    libraryTable.appendRow(["None", "None"])

# Function that handles device changes
def updateDeviceTable():
    deviceParam = videoDevice.par.device
    deviceTable.clear()

    for label, value in zip(deviceParam.menuLabels, deviceParam.menuNames):
        if value == 'csv':
            break
        deviceTable.appendRow([value, label])
    deviceTable.appendRow(["None", "None"])


# Update the tables initially
updateLibraryTable()
updateDeviceTable()

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
    alibraryTable.appendRow(["None", "None"])

# Function that handles device changes
def updateaDeviceTable():
    adeviceParam = audioDevice.par.device
    adeviceTable.clear()

    for label, value in zip(adeviceParam.menuLabels, adeviceParam.menuNames):
        adeviceTable.appendRow([value, label])
    adeviceTable.appendRow(["None", "None"])

# Update the tables initially
updateaLibraryTable()
updateaDeviceTable()