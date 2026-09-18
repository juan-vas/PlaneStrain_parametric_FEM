import numpy as np
import pandas as pd
############### INPUT ####################
new_x = [2.0, 1.0, 2.0]
new_y = [3.3, 4.023, 9.342]
node_index = [[1, 2.0, 3.3], [2, 1.0, 4.023], [3, 2.0, 9.342]]
df = pd.DataFrame(data= node_index,
                  columns= ['node_id', 'x', 'y'])


############### METHOD ###################
def prepare_grid(node_index : pd.DataFrame):
    grid_collection = []
    for row in node_index.itertuples():
        entry = "GRID,%d,0,%.7f,%.7f,0.0,0"%(row.node_id, row.x, row.y)
        grid_collection.append(entry)
    return grid_collection

############### OUTPUT ###################
result = prepare_grid(node_index = df)
print(result)
