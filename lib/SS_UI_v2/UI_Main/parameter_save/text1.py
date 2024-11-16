
table = op('testpars')
# Specify the parent path to search for TOPs
parent_path = '/SS_UI_v2/UI_Main'  # Replace with your desired path

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