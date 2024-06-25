# Get Handle to the Operators
videoDevice = op('audiodevin1')
libraryTable = op('aLibrary')
deviceTable = op('aDevice')

# Function that handles library changes
def updateLibraryTable():
    libraryParam = videoDevice.par.driver
    libraryTable.clear()

    for label, value in zip(libraryParam.menuLabels, libraryParam.menuNames):
        libraryTable.appendRow([value, label])

# Function that handles device changes
def updateDeviceTable():
    deviceParam = videoDevice.par.device
    deviceTable.clear()

    for label, value in zip(deviceParam.menuLabels, deviceParam.menuNames):
        deviceTable.appendRow([value, label])

# Update the tables initially
updateLibraryTable()
updateDeviceTable()