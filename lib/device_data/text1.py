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
adeviceTable1 = op('aDevice1')  # For audiodevin2
adeviceTable2 = op('aDevice2')  # For audiodevin3
adeviceTable3 = op('aDevice3')  # For audiodevin4

# Function that handles library changes (unchanged)
def updateaLibraryTable():
    alibraryParam = audioDevice.par.driver
    alibraryTable.clear()

    for label, value in zip(alibraryParam.menuLabels, alibraryParam.menuNames):
        alibraryTable.appendRow([value, label])
    alibraryTable.appendRow(["None", "None"])

# Function that handles device changes for each audiodevin
def updateaDeviceTable(deviceIndex):
    if deviceIndex == 1:
        deviceOp = op('audiodevin2')
        deviceTable = adeviceTable1
    elif deviceIndex == 2:
        deviceOp = op('audiodevin3')
        deviceTable = adeviceTable2
    elif deviceIndex == 3:
        deviceOp = op('audiodevin4')
        deviceTable = adeviceTable3
    else:
        return

    adeviceParam = deviceOp.par.device
    deviceTable.clear()

    for label, value in zip(adeviceParam.menuLabels, adeviceParam.menuNames):
        deviceTable.appendRow([value, label])
    deviceTable.appendRow(["None", "None"])

# Call the update functions
updateaLibraryTable()

# Run device updates for each audio device
updateaDeviceTable(1)  # For audiodevin2
updateaDeviceTable(2)  # For audiodevin3
updateaDeviceTable(3)  # For audiodevin4


# Get Handle to the Operators
audioOutDevice = op('audiodevout1')
aolibraryTable = op('aOutLibrary')
aodeviceTable = op('aOutDevice')

# Function that handles library changes
def updateaoLibraryTable():
    aolibraryParam = audioOutDevice.par.driver
    aolibraryTable.clear()

    for label, value in zip(aolibraryParam.menuLabels, aolibraryParam.menuNames):
        aolibraryTable.appendRow([value, label])
    aolibraryTable.appendRow(["None", "None"])

# Function that handles device changes
def updateaoDeviceTable():
    aodeviceParam = audioOutDevice.par.device
    aodeviceTable.clear()

    for label, value in zip(aodeviceParam.menuLabels, aodeviceParam.menuNames):
        aodeviceTable.appendRow([value, label])
    aodeviceTable.appendRow(["None", "None"])

# Update the tables initially
updateaoLibraryTable()
updateaoDeviceTable()