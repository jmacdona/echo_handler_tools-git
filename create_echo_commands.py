from itertools import product
from collections import OrderedDict
import sys

def get_well_ID(well_number):
	letters = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','','','','','','','','','','','']
	row = well_number // 24
	col = (well_number % 24) + 1
    	row_letter = letters[row] 
	return row_letter + str(col)

class InstrClass(object):
        def __init__(self, source_well, dest_well, volume, chemical, source_instantiated):
 		self.source_well = source_well
		self.dest_well = dest_well
		self.volume = volume
		self.chemical = chemical
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
src_dead_vol = 15
src_max_vol = 100


dest_final_volume = 10.0


instruction_list = []
count = 0
for condition in product(*conc_lists):
    dest_well = get_well_ID(count)
    print dest_well + "\t" +str(condition)

    total_well_vol = 0
    # loop over stocks to create instructions:
    for idx, conc in enumerate(condition):
        stock_tup = stocks.items()[idx]
	stock_chem = stock_tup[0]
	stock_conc = stock_tup[1]
	
	if conc > 0:
	    volume_to_transfer = (float(conc)/float(stock_conc)) * float(dest_final_volume)
	    instr = InstrClass("", dest_well, volume_to_transfer, stock_chem, False)
	    print "transfer: " + str(volume_to_transfer) + " from " + stock_chem + ":" + str(stock_conc) + " stock to destination well: " + dest_well + " for final conc " + str(conc)
            total_well_vol += volume_to_transfer
            #print stock_tup
	    instruction_list.append(instr)

    # finally make up volume with water:
    volume_to_transfer = dest_final_volume - total_well_vol
    instr = InstrClass("", dest_well, volume_to_transfer, "water", False)
    instruction_list.append(instr)
    print "transfer: " + str(volume_to_transfer) + " from water stock to destination well: " + dest_well + " for final volume " + str(dest_final_volume)
    if volume_to_transfer < 0:
	print "ERROR: stock concentrations are not concentrated enough - can not create instructions"
        sys.exit()
        	
    count += 1

# now need to work out source wells and volumes and finalise instructions:
stock_vols_used  = OrderedDict(stocks)
stock_vols_used["water"] = 0

for key,val in stock_vols_used.iteritems():
    stock_vols_used[key] = 0


for instr in instruction_list:
    chem = instr.chemical
    vol = instr.volume
    stock_vols_used[chem] += vol

for key,val in stock_vols_used.iteritems():
    print str(key) + " " + str(val)
    



# print instructions:
for instr in instruction_list:
    print "sourcePlate," + instr.source_well + ",destPlate," + instr.dest_well + "," + str(instr.volume)
    chem = instr.chemical
    vol = instr.volume



