# me - this DAT.
# 
# dat - the changed DAT
# rows - a list of row indices
# cols - a list of column indices
# cells - the list of cells that have changed content
# prev - the list of previous string contents of the changed cells
# 
# Make sure the corresponding toggle is enabled in the DAT Execute DAT.
# 
# If rows or columns are deleted, sizeChange will be called instead of row/col/cellChange.


def onTableChange(dat):
	return

def onRowChange(dat, rows):
	op('/globals')['a1l',1]=dat[1,2]
	op('/globals')['a1d',1]=dat[1,0]
	op('/globals')['a1',1]=dat[1,1]
	return

def onColChange(dat, cols):
	return

def onCellChange(dat, cells, prev):
	return

def onSizeChange(dat):
	return
	