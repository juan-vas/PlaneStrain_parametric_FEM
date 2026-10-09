import numpy as np
from numpy.linalg import inv

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

def get_stiffness_matrix(E1, v12, v21, E2, G12):
    q11 = E1 / (1 - v12 * v21)
    q22 = E1 * v21 / (1 - v12 * v21)
    q12 = E2 * v12 / (1 - v12 * v21)
    q22 = E2 / (1 - v12 * v21)
    q66 = G12
    stiffness_matrix = np.array([[q11, q12, 0],
                  [q12, q22, 0],
                  [0, 0, q66]])
    return stiffness_matrix

def get_transformation_matrix(angle):
    c = np.cos(angle * np.pi / 180)
    s = np.sin(angle * np.pi /180)
    t = np.array([[c**2, s**2, 2 *s*c], 
                  [s**2, c**2, -2*s*c], 
                  [-s*c, s*c, c**2 - s**2]])
    return t

def get_transformed_stiffness_matrix (transformation_matrix : np.array, stiffness_matrix : np.array):
    q_hat = inv(transformation_matrix) @ stiffness_matrix @ np.transpose(inv(transformation_matrix))
    return q_hat

def get_a_matrix(transformed_stiffness_matrix: np.array, ply_thickness : float):
    a_matrix = transformed_stiffness_matrix * ply_thickness
    return a_matrix

def rule_of_mixtures(E_fiber : float, fvf : float, E_matrix : float):
    e_1 = E_fiber * fvf + E_matrix * (1 - fvf)
    return e_1
