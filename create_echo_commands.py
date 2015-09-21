from itertools import product


stocks = {
    'ATP': 100, 
    'NAD': 100, 
    'MAD': 100}

conc_lists = [
    [0,1,2],
    [0,4,5],
    [0,6,7]
]




for items in product(*conc_lists):
    print items



