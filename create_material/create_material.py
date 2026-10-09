from create_material.interfaces import Material
import materials as m
import pandas as pd


################ METHOD ####################
def create_material(material_dict : dict, ply_thickness : float):
    material_db = pd.DataFrame(columns= ["mid", "card_type", "orientation", "material_line_1", "material_line_2"])
    base_material = Material(material_dict)
    base_material.get_resin(material_db)
    base_material.get_rotated_ply(0, ply_thickness, material_db)
    base_material.get_rotated_ply(45, ply_thickness, material_db)
    base_material.get_rotated_ply(-45, ply_thickness, material_db)
    base_material.get_rotated_ply(90, ply_thickness, material_db)
    material_db.to_csv("material_db.csv", index=False)
    return base_material





