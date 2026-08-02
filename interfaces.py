import functions as f
import gap_functions as gap_f
import numpy as np


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

        self.x_bezier_left = None
        self.y_bezier_left = None
        self.x_bezier_right = None
        self.y_bezier_right = None

        # Calculate the points of intersection
        self.center = None
        self.gap_limit_left = None
        self.gap_limit_rigth = None
        self.x_intersection_left = None
        self.x_intersection_right = None

        self.y_intersection_left_down = None
        self.y_intersection_left_up = None
        self.y_intersection_right_down = None
        self.y_intersection_right_up = None

class Ondulation(Defect):
    def __init__(self, ply_with_defect_index, defect_width, defect_type):
            super().__init__(ply_with_defect_index, defect_width, defect_type)

class Laminate:
    def __init__(self, number_of_plies : int, defect : Defect):
        self.number_of_plies = number_of_plies
        self.ply_thickness = 0.125
        self.ply_width = 5
        self.number_of_points = 500
        self.x = np.linspace(0, self.ply_width, self.number_of_points)
        ply_heigths = np.linspace(0, self.number_of_plies * self.ply_thickness, self.number_of_plies + 1)
        self.y = np.repeat(ply_heigths[:, np.newaxis], self.number_of_points, axis=1)
        self.defect = defect

def create_defect(ply_with_defect_index : int, 
                  defect_width : float,
                  defect_index : int) -> Defect:
    registry = {0: Ondulation,
                1: Gap}
    subclass = registry.get(defect_index, Defect)
    return subclass(ply_with_defect_index, defect_width, defect_index)

def apply_ondulation(Laminate: Laminate, Defect : Defect):
    x = Laminate.x
    y = Laminate.y
    gap_width = Defect.defect_width
    defect_index = Defect.ply_with_defect_index
    flawed_ply = f.get_max_ondulation(x, gap_width)
    flawed_laminate =f.apply_ondulation(y, flawed_ply, defect_index)
    Laminate.y = flawed_laminate
    return Laminate
    
def apply_gap(Laminate : Laminate, Gap : Gap):
    # Calculate points of intersection

    Gap.center = Laminate.ply_width / 2
    Gap.gap_limit_left = Gap.center - Gap.defect_width / 2
    Gap.gap_limit_rigth = Gap.center + Gap.defect_width / 2
    delta = min(max(Gap.delta_frac * Gap.defect_width, 1e-6), 0.49 * Gap.defect_width)

    Gap.x_intersection_left = Gap.gap_limit_left + delta
    Gap.x_intersection_right = Gap.gap_limit_rigth - delta

    x_points = Laminate.x
    y_points_down = Laminate.y[Gap.ply_with_defect_index - 1]
    y_points_up = Laminate.y[Gap.ply_with_defect_index]

    Gap.y_intersection_left_down = gap_f.get_gap_intersection(Gap.x_intersection_left, x_points, y_points_down)
    Gap.y_intersection_left_up = gap_f.get_gap_intersection(Gap.x_intersection_left, x_points, y_points_up)
    Gap.y_intersection_right_down = gap_f.get_gap_intersection(Gap.x_intersection_right, x_points, y_points_down)
    Gap.y_intersection_right_up = gap_f.get_gap_intersection(Gap.x_intersection_right, x_points, y_points_up)

    # Get gap curves
    k_left = gap_f.get_bisection(x0= Gap.x_intersection_left,
                                 y0= Gap.y_intersection_left_down,
                                 y1= Gap.y_intersection_left_up,
                                 dir= +1,
                                 c_gap= Gap.c_gap,
                                 smooth= Gap.smooth,
                                 xgrid= Laminate.x,
                                 y_low_vec= Laminate.y[Gap.ply_with_defect_index - 1],
                                 y_up_vec= Laminate.y[Gap.ply_with_defect_index],
                                 gap_LR= np.array([Gap.x_intersection_left, Gap.gap_limit_rigth]),
                                 tol= Gap.clearance_tolerance,
                                 npt= Gap.num_points_bezier,
                                 kmin= Gap.kmin,
                                 max_iter= Gap.max_iterations,
                                 return_frac= Gap.return_frac,
                                 eps_end_frac= Gap.eps_end_frac)

    k_right = gap_f.get_bisection(x0= Gap.x_intersection_right,
                                 y0= Gap.y_intersection_right_down,
                                 y1= Gap.y_intersection_right_up,
                                 dir= -1,
                                 c_gap= Gap.c_gap,
                                 smooth= Gap.smooth,
                                 xgrid= Laminate.x,
                                 y_low_vec= Laminate.y[Gap.ply_with_defect_index - 1],
                                 y_up_vec= Laminate.y[Gap.ply_with_defect_index],
                                 gap_LR= np.array([Gap.gap_limit_left, Gap.x_intersection_right]),
                                 tol= Gap.clearance_tolerance,
                                 npt= Gap.num_points_bezier,
                                 kmin= Gap.kmin,
                                 max_iter= Gap.max_iterations,
                                 return_frac= Gap.return_frac,
                                 eps_end_frac= Gap.eps_end_frac)
    # Force common k
    k_common = min(k_left, k_right)

    # Generate both gap borders using k_common
    x_bezier_left, y_bezier_left = gap_f.generate_spline_with_fixed_k(x0= Gap.x_intersection_left,
                                                       y0= Gap.y_intersection_left_down,
                                                       y1= Gap.y_intersection_left_up,
                                                       dir= +1,
                                                       c_gap= Gap.c_gap,
                                                       k_fixed= k_common,
                                                       smooth= Gap.smooth,
                                                       return_frac= Gap.return_frac,
                                                       eps_end_frac= Gap.eps_end_frac,
                                                       xgrid= Laminate.x,
                                                       y_up_vec= Laminate.y[Gap.ply_with_defect_index],
                                                       npt= Gap.num_points_bezier)

    x_bezier_right, y_bezier_right = gap_f.generate_spline_with_fixed_k(x0= Gap.x_intersection_right,
                                                       y0= Gap.y_intersection_right_down,
                                                       y1= Gap.y_intersection_right_up,
                                                       dir= -1,
                                                       c_gap= Gap.c_gap,
                                                       k_fixed= k_common,
                                                       smooth= Gap.smooth,
                                                       return_frac= Gap.return_frac,
                                                       eps_end_frac= Gap.eps_end_frac,
                                                       xgrid= Laminate.x,
                                                       y_up_vec= Laminate.y[Gap.ply_with_defect_index],
                                                       npt= Gap.num_points_bezier)

    Gap.x_bezier_left = x_bezier_left
    Gap.y_bezier_left = y_bezier_left
    Gap.x_bezier_right = x_bezier_right
    Gap.y_bezier_right = y_bezier_right

    # Check for mistakes:
    print(Gap.gap_limit_left)           # ok
    print(Gap.gap_limit_rigth)          # ok
    print(delta)                        # ok
    print(Gap.x_intersection_left)      # ok
    print(Gap.x_intersection_right)     # ok
    print(Gap.y_intersection_left_down) # ok
    print(Gap.y_intersection_left_up)   # ok
    print(Gap.y_intersection_right_down)# ok
    print(Gap.y_intersection_right_up)  # ok







def plot_geometry(Laminate:Laminate):
    x = Laminate.x
    y = Laminate.y
    defect = Laminate.defect
    if isinstance(Laminate.defect, Gap):
        x_left = defect.x_bezier_left
        y_left = defect.y_bezier_left
        x_right = defect.x_bezier_right
        y_right = defect.y_bezier_right

    f.plot_geometry(x, y, x_left, y_left, x_right, y_right)