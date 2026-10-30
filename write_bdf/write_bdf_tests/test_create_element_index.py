import pandas as pd
################ INPUT ##########################
node_index = pd.read_csv('sample_node_index.csv', sep= ';')
curve_a = node_index[node_index['curve_id'] == 0].reset_index(drop= True)
curve_b = node_index[node_index['curve_id'] == 1].reset_index(drop= True)
ply_index = pd.read_csv('sample_ply_index.csv', sep= ';')
element_index= pd.DataFrame(columns=["element_id", "pid", "node_a", "node_b", "node_c", "node_d", "local_thickness", "fvf"])

cquad_collection = []

bottom_curve = curve_a.loc[0,'curve_id']
corresponding_ply = ply_index[ply_index['bottom_curve_id'] == bottom_curve]
pid = corresponding_ply.loc[0,'pid']

fvf_0 = 0.6
ply_thickness_0 = 0.125

################ METHOD #########################
def create_element_index(curve_a : pd.DataFrame, curve_b : pd.DataFrame, element_index : pd.DataFrame, pid : int, ply_thickness, fvf_0):
    element_id = len(element_index) + 1
    number_of_nodes_per_curve = curve_a.shape[0]
    counter = 0
    while counter < number_of_nodes_per_curve - 1:
        a = curve_a.loc[counter, 'node_id']
        b = curve_a.loc[counter + 1, 'node_id']
        c = curve_b.loc[counter + 1, 'node_id']
        d = curve_b.loc[counter, 'node_id']

        # Calculate local thickness 
        y_a = float(curve_a.loc[counter, 'y'])
        y_b = float(curve_a.loc[counter + 1, 'y'])
        y_c = float(curve_b.loc[counter + 1, 'y'])
        y_d = float(curve_b.loc[counter, 'y'])

        local_thickness = ( (y_d - y_a) + (y_c - y_b) ) / 2
        
        # Calculate local fiber volume fraction
        fvf = fvf_0 * ply_thickness / 3 / local_thickness
        fvf = round(fvf, 3)

        db_entry = [element_id, pid, a, b, c, d, local_thickness, fvf]
        element_index.loc[len(element_index)] = db_entry

        element_id += 1
        counter += 1

################ OUTPUT #########################
create_element_index(curve_a, curve_b, element_index, pid, ply_thickness_0, fvf_0)
element_index = element_index.astype({'element_id' : int,
                'pid' : int,
                'node_a' : int,
                'node_b' : int,
                'node_c' : int,
                'node_d' : int,
                'local_thickness' : float,
                'fvf' : float
                })

element_index.to_csv('sample_element_index.csv')