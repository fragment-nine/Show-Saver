def stampToInt(stamp):
    parts = [p for p in re.split(r'[:;]', str(stamp).strip()) if p != '']
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
