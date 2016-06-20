from itertools import product
from collections import OrderedDict
import sys

def get_well_ID(well_number, plate_type):
	row = 0
	col = 0
	num_rows = 0
	letters = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','AA', 'AB', 'AC', 'AD', 'AE', 'AD', 'AE', 'AF' ]
	
	if (plate_type == "384"):
		num_rows = 24
	elif (plate_type == "1536"):
		num_rows = 48
	elif (plate_type == "96"):
		num_rows = 12
	else:
		print "ERROR: plate type not recognised"
		sys.exit()
	row = well_number // num_rows
	col = (well_number % num_rows) + 1
    	row_letter = letters[row] 
	return (row_letter + str(col), row_letter, str(col))

class InstrClass(object):
        def __init__(self, source_well, dest_well, volume, chemical, source_instantiated):
 		self.source_well = source_well
		self.dest_well = dest_well
		self.volume = volume
		self.chemical = chemical
		self.source_instantiated = source_instantiated
		return


# START of user defineable parameters

# all concs in mM
stocks = OrderedDict([
    ('ATP', 100), 
    ('NAD', 100), 
    ('MAD', 100), 
    ])

# these must be in the same order as declared in stocks dictionary
conc_lists = [
    [0,1,2,3,4,5],			# ATP concs
    [0,4,5,6,7,8],			# NAD concs
    [0,6,7,8,9,10]			# MAD concs
]

# define plate type
src_plate_type = "384"
dest_plate_type = "1536"


# all volumes in uL
src_dead_vol = 15
src_max_vol = 65
transferable_vol = src_max_vol - src_dead_vol

dest_final_volume = 10.0

# END of user defineable stuff





instruction_list = []
count = 0

sys.stdout.write("CONDITION," + "DEST_ROW" + "," + "DEST_COL" + "," + "DEST_WELL"  )
for stock in stocks:
   sys.stdout.write("," + str(stock))
sys.stdout.write("\n")

for condition in product(*conc_lists):
    (dest_well, dest_row, dest_col) = get_well_ID(count, dest_plate_type)
    #print "CONDITION," + dest_well + "," +str(condition)
    sys.stdout.write("CONDITION," + dest_row + "," + dest_col + "," + dest_well  )
    for conc in condition:
        sys.stdout.write("," + str(conc) )
    sys.stdout.write("\n")

    total_well_vol = 0
    # loop over stocks to create instructions:
    for idx, conc in enumerate(condition):
        stock_tup = stocks.items()[idx]
	stock_chem = stock_tup[0]
	stock_conc = stock_tup[1]
	
	if conc > 0:
	    volume_to_transfer = (float(conc)/float(stock_conc)) * float(dest_final_volume)
	    instr = InstrClass("", dest_well, volume_to_transfer, stock_chem, False)
	    #print "transfer: " + str(volume_to_transfer) + " from " + stock_chem + ":" + str(stock_conc) + " stock to destination well: " + dest_well + " for final conc " + str(conc)
            total_well_vol += volume_to_transfer
            #print stock_tup
	    instruction_list.append(instr)

    # finally make up volume with water:
    volume_to_transfer = dest_final_volume - total_well_vol
    if volume_to_transfer > 0:
        instr = InstrClass("", dest_well, volume_to_transfer, "water", False)
        instruction_list.append(instr)
    #print "transfer: " + str(volume_to_transfer) + " from water stock to destination well: " + dest_well + " for final volume " + str(dest_final_volume)
    if volume_to_transfer < 0:
	print "ERROR: stock concentrations are not concentrated enough - can not create instructions"
        sys.exit()
        	
    count += 1

# now need to work out source wells and volumes and finalise instructions:
stock_vols_used  = OrderedDict(stocks)
stock_vols_used["water"] = 0
for key,val in stock_vols_used.iteritems():
    stock_vols_used[key] = 0

# find maximum volume transferred to add safety margin
max_vol_used =  OrderedDict(stocks)
max_vol_used["water"] = 0
for key,val in max_vol_used.iteritems():
    max_vol_used[key] = 0


# calculate volumes used
for instr in instruction_list:
    chem = instr.chemical
    vol = instr.volume
    stock_vols_used[chem] += vol
    if vol > max_vol_used[chem]:
	max_vol_used[chem] = vol


# work out number of source wells needed:
src_instruction_list = []
src_chem_well_volume_acc = {}
well_num = 0
for chem,total_vol in stock_vols_used.iteritems():
    # print str(chem) + " " + str(total_vol)
    # add max volume safety margin
    safety_count = (total_vol // transferable_vol) + 1
    total_vol += (safety_count) * max_vol_used[chem]
    #print str(chem) + " " + str(total_vol)

    num_wells_needed = int(total_vol // transferable_vol)
    if float(total_vol)%float(transferable_vol) > 0:
	num_wells_needed += 1
    #print str(well_num) + " " + str(num_wells_needed)

    vol_acc = total_vol
    chem_well_volume_acc = OrderedDict()
    for ii in range(well_num, well_num+num_wells_needed):
	src_well = get_well_ID(ii, src_plate_type)[0]
        volume_to_transfer = src_dead_vol
        if vol_acc >= transferable_vol:
		volume_to_transfer += transferable_vol
	else:
		volume_to_transfer += vol_acc
        instr = InstrClass(src_well, "", volume_to_transfer, chem, False)
        vol_acc -= (volume_to_transfer - src_dead_vol)
	chem_well_volume_acc[src_well] = volume_to_transfer
	src_instruction_list.append(instr)
    src_chem_well_volume_acc[chem] = chem_well_volume_acc
    well_num += num_wells_needed

#print src_chem_well_volume_acc
print

# calculate source wells
for instr in instruction_list:
    chem = instr.chemical
    vol = instr.volume
    src_wells = src_chem_well_volume_acc[chem]
    well_found = False
    found_well = ""
    for well,vol_avail in src_wells.iteritems():
	# this was vol <= (vol_avail - src_dead_vol) but this causes bugs
    	if vol <= (vol_avail - src_dead_vol):
    		well_found = True
    		found_well = well
    		break
    if well_found == True:
        src_wells[found_well] -= vol
	instr.source_well = found_well
    else:
	print "ERROR: bug finding available well!"
	sys.exit()

#print src_chem_well_volume_acc    

print "Source Plate Barcode,Source Well,Destination Plate Barcode,Destination Well,Transfer Volume"
# print instructions:
for instr in instruction_list:
    chem = instr.chemical
    vol = instr.volume
    print "sourcePlate," + instr.source_well + ",destPlate," + instr.dest_well + "," + str(instr.volume*1000.) + ",#" + chem

print
#print source instructions:
for instr in src_instruction_list:
	conc = 55500
	if instr.chemical != 'water':
		conc = stocks[instr.chemical]
	print "SOURCE_PREP: add " + str(instr.volume) + " uL of " + str(conc) + " mM " + instr.chemical  + " to well " + instr.source_well + " in source plate"



