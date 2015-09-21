from itertools import product


def get_well_ID(well_number):
	letters = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','','','','','','','','','','','']
	row = well_number // 24
	col = (well_number % 24) + 1
    	row_letter = letters[row] 
	return row_letter + str(col)


stocks = {
    'ATP': 100, 
    'NAD': 100, 
    'MAD': 100}

conc_lists = [
    [0,1,2],
    [0,4,5],
    [0,6,7]
]




count = 0
for items in product(*conc_lists):
    dest_well = get_well_ID(count)
    print dest_well + "\t" +str(items)
	
    count += 1



