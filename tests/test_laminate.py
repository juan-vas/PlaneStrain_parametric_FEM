import numpy as np

########### INPUT ############
number_of_plies = 4

########## METHOD ############

class Laminate:
    def __init__(self, number_of_plies : int):
        self.number_of_plies = number_of_plies
        self.ply_thickness = 0.125
        self.ply_width = 5
        self.number_of_points = 500
        self.x = np.linspace(0, self.ply_width, self.number_of_points)
        ply_heigths = np.linspace(0, self.number_of_plies * self.ply_thickness, self.number_of_plies + 1)
        self.y = np.repeat(ply_heigths[:, np.newaxis], self.number_of_points, axis=1)
        self.defect = None
            

########## OUTPUT ###############

pristine_laminate = Laminate(number_of_plies)
result = pristine_laminate.y
print(result)

    