from itertools import product
from collections import OrderedDict

def get_well_ID(well_number):
	letters = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','','','','','','','','','','','']
	row = well_number // 24
	col = (well_number % 24) + 1
    	row_letter = letters[row] 
	return row_letter + str(col)

class InstrClass(object):
        def __init__(self, source_well, dest_well, volume, source_instantiated):
 		self.source_well = source_well
		self.dest_well = dest_well
		self.volume = volume
		self.source_instantiated = source_instantiated
		return

# all concs in mM
stocks = OrderedDict([
    ('ATP', 100), 
    ('NAD', 100), 
    ('MAD', 100), 
    ])

# these must be in the same order as declared in stocks dictionary
conc_lists = [
    [0,1,2],			# ATP concs
    [0,4,5],			# NAD concs
    [0,6,7]			# MAD concs
]

# all volumes in uL
dest_final_volume = 10


instruction_list = []
count = 0
for condition in product(*conc_lists):
    dest_well = get_well_ID(count)
    print dest_well + "\t" +str(condition)

    # loop over stocks to create instructions
    for idx, val in enumerate(condition):
        stock_tup = stocks.items()[idx]
	stock_chem = stock_tup[0]
	stock_conc = stock_tup[1]

	instr = InstrClass("", dest_well, 0, False)
        print stock_tup
	instruction_list.append(instr)
        	
    count += 1



