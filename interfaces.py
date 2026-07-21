import functions as f
import numpy as np

class Laminate:
    def __init__(self, number_of_plies : int):
        self.number_of_plies = number_of_plies
        self.ply_thickness = 0.125
        self.ply_width = 5
        self.number_of_points = 500
        self.x = np.linspace(0, self.ply_width, self.number_of_points)
        ply_heigths = np.linspace(0, self.number_of_plies * self.ply_thickness, self.number_of_plies + 1)
        self.y = np.repeat(ply_heigths[:, np.newaxis], self.number_of_points, axis=1)

def apply_defect(Laminate: Laminate, defect_width, defect_index):
    x = Laminate.x
    y = Laminate.y
    gap_width = defect_width
    flawed_ply = f.get_max_ondulation(x, gap_width)
    flawed_laminate =f.apply_defect(y, flawed_ply, defect_index)
    Laminate.y = flawed_laminate
    return Laminate
    




def plot_geometry(Laminate:Laminate):
    x = Laminate.x
    y = Laminate.y
    f.plot_geometry(x, y)