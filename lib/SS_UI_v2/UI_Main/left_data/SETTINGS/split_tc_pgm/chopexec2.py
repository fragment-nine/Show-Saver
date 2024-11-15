def valueChange(channel, sampleIndex, val, prev):
    # Check if the channel is 'postroll'
    if channel.name == 'postroll':
        # Reference the table DAT you want to modify
        table = op('/globals')  # Update with your correct table DAT path
 

        target_row = 10
        target_col = 1   
        
        # Update the table with the 'postroll' value
        table[target_row, target_col] = str(val)  # Convert the value to string for the table
    
    return
