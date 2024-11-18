# me - this DAT
# 
# frame - the current frame
# state - True if the timeline is paused
# 
# Make sure the corresponding toggle is enabled in the Execute DAT.

def onStart():
    # Restore script logic here
    comp_path = '/SS_UI_v2/UI_Main'  # Replace with your parent path
    table = op('parameter_table')  # Replace with your Table DAT's path

    # Iterate through table rows and apply the stored values
    for row in table.rows()[1:]:  # Skip the header row
        top_path = row[0].val
        param_name = row[1].val
        param_value = row[2].val

        # Ensure the TOP exists and has the parameter
        top = op(top_path)
        if top and hasattr(top.par, param_name):
            try:
                setattr(top.par, param_name, eval(param_value))  # Convert to proper type
            except:
                setattr(top.par, param_name, param_value)  # Fallback for string values
    return

def onCreate():
	return

def onExit():
	return

def onFrameStart(frame):
	return

def onFrameEnd(frame):
	return

def onPlayStateChange(state):
	return

def onDeviceChange():
	return

def onProjectPreSave():
	# Save script logic here
    comp_path = '/SS_UI_v2/UI_Main'  # Replace with your parent path
    table = op('parameter_table')  # Replace with your Table DAT's path

    # Clear existing table content
    table.clear()
    table.appendRow(['OP Path', 'Parameter Name', 'Value'])  # Add headers

    # Function to find all TOPs recursively
    def find_all_tops(op_path):
        return [op for op in op(op_path).findChildren()]

    # Iterate through all TOPs and store 'Value0' parameters
    for top in find_all_tops(comp_path):
        if hasattr(top.par, 'Value0'):  # Check if 'Value0' parameter exists
            table.appendRow([top.path, 'Value0', top.par.Value0.eval()])
    return

def onProjectPostSave():
	return

	