import pandas as pd

############# INPUT #################
material_index = pd.read_csv("material_db.csv")
print(material_index)

############## METHOD ################
def prepare_nastran_materials(material_index : pd.DataFrame):
    material_collection = []
    bdf_line_1 = material_index['material_line_1'].tolist()
    bdf_line_2 = material_index['material_line_2'].tolist()
    i = 0
    while i < len(bdf_line_1):
        material_collection.append(bdf_line_1[i])
        material_collection.append(bdf_line_2[i])
        i += 1
    return material_collection

############## OUTPUT ################
result = prepare_nastran_materials(material_index)
print(result)
