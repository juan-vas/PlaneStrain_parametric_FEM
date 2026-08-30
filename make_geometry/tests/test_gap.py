import test_defect
from test_defect import Defect
########### INPUT ############

# Defect object:
ply_with_defect_index = 4
defect_width = 0.5
# Defect Type
## Ondulation   : 0
## Gap          : 1
defect_type = 1
sample_defect = test_defect.Defect(ply_with_defect_index, defect_width, defect_type)


########### METHOD #############
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
        self.k_common = None

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

########### OUTPUT #############
gap = Gap(ply_with_defect_index, defect_width, defect_type)
print(gap.delta_frac)