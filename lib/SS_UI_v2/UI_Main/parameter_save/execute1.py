# me  - this DAT
# frame - the current frame
# state - True if the timeline is paused
#
# Toggle the corresponding check-boxes on this Execute DAT as needed.

# -------------------------------------------------------------------------
# Helper
# -------------------------------------------------------------------------

def _is_selected_cell(path_or_op):
    """
    Return True if the OP’s *name* is exactly 'selectedCell'
    or the *path* contains '/selectedCell'.
    Works for either a string path or an OP object.
    """
    if isinstance(path_or_op, str):
        return '/selectedCell' in path_or_op
    else:
        return path_or_op.name == 'selectedCell'

# -------------------------------------------------------------------------
# Callbacks
# -------------------------------------------------------------------------

def onStart():
    """
    Restore parameter values from parameter_table when the .toe opens,
    except for anything called selectedCell.
    """
    table = op('parameter_table')          # Table DAT that stores the data

    # iterate over each stored row (skip the header)
    for row in table.rows()[1:]:
        op_path, param_name, param_value = row[0].val, row[1].val, row[2].val

        # *** skip selectedCell ***
        if _is_selected_cell(op_path):
            continue

        target = op(op_path)
        if not target:
            continue
        if not hasattr(target.par, param_name):
            continue

        try:
            # convert strings like '1.0' / 'True' / 'op("geo1")' etc.
            setattr(target.par, param_name, eval(param_value))
        except Exception:
            setattr(target.par, param_name, param_value)  # treat as plain string

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
    """
    Walk UI hierarchy, capture Value0/value0 parameters **except** selectedCell,
    and store them to parameter_table so they persist across launches.
    """
    comp_path = '/SS_UI_v2/UI_Main'        # root of the UI tree
    table = op('parameter_table')          # where we store results

    # clear and write headers
    table.clear()
    table.appendRow(['OP Path', 'Parameter Name', 'Value'])

    # scan every descendant COMP
    for target in op(comp_path).findChildren():

        # *** skip selectedCell ***
        if _is_selected_cell(target):
            continue

        # look for either capitalisation of Value0
        for pname in ('Value0', 'value0'):
            if hasattr(target.par, pname):
                p = getattr(target.par, pname)
                try:
                    val = p.eval()
                except Exception:
                    val = p.val
                table.appendRow([target.path, pname, val])

    return


def onProjectPostSave():
    return