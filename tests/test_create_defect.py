import numpy as np

############### INPUT #############
number_of_plies = 8
ply_with_defect_index = 4
defect_width = 0.5
# Defect Type
## Ondulation   : 0
## Gap          : 1
defect_type = 0


class Laminate:
    def __init__(self, number_of_plies : int):
        self.number_of_plies = number_of_plies
        self.ply_thickness = 0.125
        self.ply_width = 5
        self.number_of_points = 500
        self.x = np.linspace(0, self.ply_width, self.number_of_points)
        ply_heigths = np.linspace(0, self.number_of_plies * self.ply_thickness, self.number_of_plies + 1)
        self.y = np.repeat(ply_heigths[:, np.newaxis], self.number_of_points, axis=1)

class Defect:
    def __init__(self, ply_with_defect_index: int, defect_width: float, defect_type: int):
        self.ply_with_defect_index = ply_with_defect_index
        self.defect_width = defect_width
        self.defect_type = defect_type

    def display_defect_type(self):
        if self.defect_type == 0:
            print("The Laminate has an Ondulation Defect")
        if self.defect_type == 1:
            print("The Laminate has a Gap defect")

class Gap(Defect):
    def __init__(self, ply_with_defect_index, defect_width, defect_type):
        super().__init__(ply_with_defect_index, defect_width, defect_type)
        # Gap properties:
        self.delta_frac = 0.12
        self.c_gap = 0.95 * defect_width
        self.smooth = 0.3
        self.return_frac = 0.85
        self.eps_end_frac = 0.03
        self.clearance_tolerance = 0.002
        self.num_points_bezier = 600
        self.kmin = 0.35
        self.max_iterations = 28
        self.bezier_curves = None
        
class Ondulation(Defect):
    def __init__(self, ply_with_defect_index, defect_width, defect_type):
            super().__init__(ply_with_defect_index, defect_width, defect_type)

############### METHOD ##############

def create_defect(ply_with_defect_index : int, 
                  defect_width : float,
                  defect_index : int) -> Defect:
    registry = {0: Ondulation,
                1: Gap}
    subclass = registry.get(defect_index, Defect)
    return subclass(ply_with_defect_index, defect_width, defect_index)

########### OUTPUT #################
defect = create_defect(ply_with_defect_index, defect_width, defect_type)
result = type(defect).__name__
print(result)