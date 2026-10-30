import pandas as pd
from create_material.interfaces import Material
import materials as m
import copy

material = m.hexply_8552_ud
base_material = Material(material_dict= material)
ply_thickness = 0.125

element_index = pd.read_csv('sample_element_index.csv')
ply_index = pd.read_csv('sample_ply_index.csv', sep= ';')
material_index = pd.read_csv('material_db.csv')
property_index = pd.read_csv('sample_property_index.csv')
#print(element_index.head(1))
#print(ply_index.head(1))
# print(material_index.head(1))

#################################### METHOD ######################################
def update_material(material : Material, element_index : pd.DataFrame, 
                    ply_index : pd.DataFrame, material_index : pd.DataFrame,
                    property_index : pd.DataFrame, ply_thickness
                    ):
    fvf_original = material.fvf
    df_orientations = ply_index[['fiber_angle', 'pid']]
    element_index = pd.merge(
        left= element_index,
        right= df_orientations,
        how= 'inner',
        on= 'pid'
    )

    pid = 201 # Property code for modified property
    mid = 2001
    for row in element_index.itertuples():
        if (element_index.loc[row[0], 'fvf'] != fvf_original) & (int(element_index.loc[row[0], 'pid']) < 200):
            new_fvf = element_index.loc[row[0], 'fvf']
            fiber_angle = int(element_index.loc[row[0], 'fiber_angle'])
            new_material = copy.copy(material)
            new_material.modify_by_fvf(new_fvf)
            new_material.mid = mid
            new_material.get_rotated_ply(fiber_angle, ply_thickness, material_index)
            new_property_name = f"PLY_{fiber_angle:02d}_deg FVF_{new_fvf}"
            new_property = [pid, new_property_name, new_material.mid, ply_thickness]
            property_index.loc[len(property_index)] = new_property
            element_index.loc[element_index[element_index['fvf'] == new_fvf].index, 'pid'] = pid
            pid += 1
            mid += 1
    return element_index

################################## OUTPUT ##############################################

result = update_material(base_material, element_index, ply_index, material_index, property_index, ply_thickness)
# print(result.tail(100))

print(property_index.tail())
# print(material_index.tail())
