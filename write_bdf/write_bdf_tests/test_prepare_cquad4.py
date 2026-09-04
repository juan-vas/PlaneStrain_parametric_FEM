import pandas as pd
################ INPUT ##########################
node_index = pd.read_csv('sample_node_index.csv', sep= ';')
curve_a = node_index[node_index['curve_id'] == 0].reset_index(drop= True)
curve_b = node_index[node_index['curve_id'] == 1].reset_index(drop= True)
ply_index = pd.read_csv('sample_ply_index.csv', sep= ';')
cquad_collection = []

bottom_curve = curve_a.loc[0,'curve_id']
corresponding_ply = ply_index[ply_index['bottom_curve_id'] == bottom_curve]
pid = corresponding_ply.loc[0,'pid']

################ METHOD #########################
def prepare_cquad4(curve_a : pd.DataFrame, curve_b : pd.DataFrame, cquad_collection : list, pid : int):
    element_id = len(cquad_collection) + 1
    number_of_nodes_per_curve = curve_a.shape[0]
    counter = 0
    while counter < number_of_nodes_per_curve - 1:
        a = curve_a.loc[counter, 'node_id']
        b = curve_a.loc[counter + 1, 'node_id']
        c = curve_b.loc[counter + 1, 'node_id']
        d = curve_b.loc[counter, 'node_id']
        entry = 'CQUAD4,%d,%d,%d,%d,%d,%d'%(element_id, pid, a, b, c, d)
        element_id += 1
        counter += 1
        cquad_collection.append(entry)
    return cquad_collection

################ OUTPUT #########################
result = prepare_cquad4(curve_a, curve_b, cquad_collection, pid)
print(result)
