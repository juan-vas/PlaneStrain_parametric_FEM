from create_material import functions as f
import pandas as pd
import numpy as np
from numpy.linalg import inv

class Material:
    def __init__(self, material_dict : dict):
        self.mid = 1000
        self.card_type = "MAT8"
        self.name = material_dict["name"]
        self.fiber = material_dict["fiber"]
        self.matrix = material_dict["matrix"]
        self.e1 = material_dict["E_1"]
        self.e2 = material_dict["E_2"]
        self.mu12 = material_dict["mu12"]
        self.g12 = material_dict["G_12"]
        self.g1z = material_dict["G_1z"]
        self.g2z = material_dict["G_2z"]
        self.rho = material_dict["rho"]
        self.fvf = material_dict["FVF"]
        self.e_m = material_dict["E_m"]
        self.rho_m = material_dict["rho_m"]

    def get_resin(self, material_db : pd.DataFrame):
        database_entry = f.get_mat1_card(mid= 1, stiffness= self.e_m, name= self.matrix)
        material_db.loc[len(material_db)] = database_entry

    def get_rotated_ply(self, orientation : int, ply_thickness : float, material_db : pd.DataFrame):
        e1 = self.e1
        v12 = self.mu12
        e2 = self.e2
        v21 = e2 / e1 * v12
        g12 = self.g12
        stiffness_matrix = f.get_stiffness_matrix(e1, v12, v21, e2, g12)
        transformation_matrix = f.get_transformation_matrix(angle= orientation)
        transformed_stiffness_matrix = f.get_transformed_stiffness_matrix(transformation_matrix, stiffness_matrix)
        a_matrix = f.get_a_matrix(transformed_stiffness_matrix, ply_thickness)
        a_inv = inv(a_matrix)
        e1 = 1 / a_inv[0,0] / ply_thickness
        e2 = 1 / a_inv[1,1] / ply_thickness
        g12 = 1 / a_inv[2,2] / ply_thickness
        mu12 = - a_inv[0,1] / a_inv[0,0]
        self.mid = self.mid + 1
        database_entry = f.get_mat_8_card(self.mid,
                                          e1,
                                          e2,
                                          mu12,
                                          g12,
                                          self.g1z,
                                          self.g2z,
                                          self.rho,
                                          orientation,
                                          name= self.name)
        material_db.loc[len(material_db)] = database_entry
        