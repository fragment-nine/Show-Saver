import re

def timecodeToHHMMSS(stamp):
    """
    Parse timecode from HH:MM:SS, HH:MM:SS:FF, or HH;MM;SS;FF (drop frames).
    Returns HH:MM:SS with zero-padded hours, minutes, and seconds.
    """
    raw = str(stamp).strip()
    if not raw:
        return ''
    parts = [p for p in re.split(r'[:;]', raw) if p != '']
    if not parts:
        return ''
    if len(parts) >= 4:
        h, m, s, _f = parts[0], parts[1], parts[2], parts[3]
    elif len(parts) == 3:
        h, m, s = parts
    elif len(parts) == 2:
        h, m, s = '0', parts[0], parts[1]
    else:
        h, m, s = '0', '0', parts[0]

    try:
        hi = int(h or 0)
        mi = int(m or 0)
        si = int(s or 0)
    except ValueError:
        return raw

    return f'{hi:02d}:{mi:02d}:{si:02d}'

def stampToInt(stamp):
    parts = [p for p in re.split(r'[:;]', str(stamp).strip()) if p != '']
    if not parts:
        return 0
    if len(parts) == 4:
        h, m, s, f = parts
    elif len(parts) == 3:
        h, m, s = parts; f = '0'
    elif len(parts) == 2:
        h, m, s, f = '0', parts[0], parts[1], '0'
    else:  # len == 1
        h, m, s, f = '0', '0', parts[0], '0'

    total = int(h or 0)*3600 + int(m or 0)*60 + int(s or 0)
    return total  # add frames/fps if you need fractional seconds
