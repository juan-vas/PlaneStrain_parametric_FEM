import numpy as np
import pandas as pd

############ INPUT ##############
node_index = [[1, 2.0, 3.3], [2, 1.0, 4.023], [3, 2.0, 9.342],
              [4, 2.0, 3.3], [5, 1.0, 4.023], [6, 2.0, 9.342],
              [7, 2.0, 3.3], [8, 1.0, 4.023], [9, 2.0, 9.342],]
df = pd.DataFrame(data = node_index,
                  columns= ['node_id', 'x', 'y'])
set_id = ['900100', 'ALL_NODES']

############ METHOD #############
def prepare_set(node_index : pd.DataFrame, set_id: list):
    set_number = set_id[0]
    set_label = set_id[1]
    set_collection = []
    a = f'$HMSET {set_number} 1 "{set_label}" 18'
    b = '$HMSETTYPE 1 "non-ordered" 18'
    c = f'SET,{set_number},GRID,LIST'
    set_collection.append(a)
    set_collection.append(b)
    set_collection.append(c)
    number_of_nodes = len(node_index)
    d = '+,'
    i = 0
    for row in node_index.itertuples():
        d = d + '%d,'%(row.node_id) 
        if (i + 1) % 8 == 0:
            d = d + '\n+,'
        i += 1
    set_collection.append(d)
    return set_collection

############ OUTPUT #############
result = prepare_set(node_index= df, set_id= set_id)
print(result)
