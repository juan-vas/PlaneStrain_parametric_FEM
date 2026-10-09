import numpy as np
import pandas as pd

################### INPUT ########################
hexply_8552_ud = {"name": "HexPly 8552 UD",
            "fiber": "AS4 UD",
            "matrix" : "Hexcel 8552",
            "E_1" : 127300,
            "E_2" : 9240,
            "mu12" : 0.302,
            "G_12" : 4830,
            "G_1z" : 4830,
            "G_2z" : 3600,
            "rho" : 1.59e-9,
            "FVF" : 0.6,
            "E_m" : 4670,
            "rho_m" : 1.30e-9
            }
material = hexply_8552_ud
material_id = 1
card_type = "MAT1"
stiffness_m = material["E_m"]
matrix = "Hexcel 8552"

#################### METHOD ######################
def get_mat1_card(mid, stiffness, name):
    card_type = "MAT1"
    material_line_1 = f"{card_type},{mid},{stiffness},0,0.35"
    material_line_2 = f'$HMNAME MAT {mid} "{name}"'
    material_db_entry = [mid, card_type, 0,material_line_1, material_line_2]
    return material_db_entry

def get_mat_8_card(mid : int, e1, e2, nu12, g12, g1z, g2z, rho, orientation : int, name):
    name = f'{name}_{orientation:02d} deg'
    card_type = "MAT8"
    material_line_1 = f"{card_type},{mid},{e1},{e2},{nu12},{g12},{g1z},{g2z},{rho}"
    material_line_2 = f'$HMNAME MAT {mid} "{name}"'
    material_db_entry = [mid, card_type, orientation, material_line_1, material_line_2]
    return material_db_entry

################### OUTPUT ######################
a = get_mat1_card(1, stiffness_m, name= matrix)
print(a)

b = get_mat_8_card(1001, 
                   e1 = material["E_1"],
                   e2= material["E_2"],
                   nu12= material["mu12"],
                   g12= material["G_12"],
                   g1z= material["G_1z"],
                   g2z= material["G_2z"],
                   rho= material["rho"],
                   orientation= 0,
                   name= "AS4"
                   )
print(b)
