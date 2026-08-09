############# INPUT ##############
collection = []
new_x = [2.0, 1.0, 2.0]
new_y = [3.3, 4.023, 9.342]

############ METHOD #############
def prepare_nastran_grid(new_x : list, new_y : list, grid_collection : list):
    id = len(grid_collection) + 1
    i = 0
    for element in new_x:
        entry = "GRID,%d,%.10g,%.10g,0.0"%(id, new_x[i], new_y[i])
        grid_collection.append(entry)
        id += 1
        i += 1

    return grid_collection

############ OUTPUT #############
output = prepare_nastran_grid(new_x, new_y, collection)
result = output
print(result)
