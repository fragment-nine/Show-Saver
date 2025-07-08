def onValueChange(channel, sampleIndex, val, prev):
    button_value = val  # Use the value from the CHOP triggering the CHOP Execute

    pgm_operators = [
        op('/project1/files_out/file_pgm'),
        op('/project1/files_out/file_long_pgm')
    ]
    ltc_operators = [
        op('/project1/files_out/file_ltc'),
        op('/project1/files_out/file_long_ltc')
    ]

    pgm_dat = op('/SS_UI_v2/UI_Main/left_data/AUDIO/split_tc_pgm/null2')
    ltc_dat = op('/SS_UI_v2/UI_Main/left_data/AUDIO/split_tc_pgm/null1')

    if not pgm_dat or not ltc_dat:
        print("Error: DAT operators not found.")
        return

    if button_value == 0:
        # Use the full path for the track master operator's name DAT
        track_master_name_op = op('/project1/track_master/name')

        if track_master_name_op is None:
            print("Error: '/project1/track_master/name' operator not found.")
            return

        # Check if the '/globals' operator exists
        globals_op = op('/globals')

        if globals_op is None:
            print("Error: '/globals' operator not found.")
            return

        # Check if the cells have valid values
        output_folder = globals_op['outputFolder', 1]
        track_name = track_master_name_op[0, 0]  # Fetch the name value

        if output_folder is None or track_name is None:
            print("Error: Missing values in '/globals' or 'track_master/name'.")
            return

        pgm_path = f"{output_folder.val}/{track_name.val}_pgm.mov"
        ltc_path = f"{output_folder.val}/{track_name.val}_ltc.mov"

        for op_pgm in pgm_operators:
            if op_pgm:
                op_pgm.par.file = pgm_path
                print(f"Set {op_pgm.name} to {pgm_path}")

        for op_ltc in ltc_operators:
            if op_ltc:
                op_ltc.par.file = ltc_path
                print(f"Set {op_ltc.name} to {ltc_path}")

    elif button_value == 1:
        for op_pgm in pgm_operators:
            if op_pgm:
                new_path = pgm_dat[0, 1].val
                op_pgm.par.file = new_path
                print(f"Set {op_pgm.name} to {new_path}")

        for op_ltc in ltc_operators:
            if op_ltc:
                new_path = ltc_dat[0, 1].val
                op_ltc.par.file = new_path
                print(f"Set {op_ltc.name} to {new_path}")

    return
