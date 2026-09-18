from make_geometry import functions as f
from make_geometry import interfaces as i
import numpy as np

############### METHOD #################
def make_geometry(target_directory, number_of_plies, ply_with_defect_index, defect_width, defect_type):
    i.check_input_validity(number_of_plies, ply_with_defect_index, defect_width, defect_type)
    defect = i.create_defect(ply_with_defect_index, defect_width, defect_type)
    laminate = i.Laminate(number_of_plies, defect)
    if defect_width != 0:
        laminate = i.apply_ondulation(laminate, defect)
        if defect.defect_type == 1: i.apply_gap(laminate, defect)
    ax = i.plot_geometry(laminate, target_directory)
    i.create_auxiliary_curves(laminate, target_directory, ax)
    return laminate

############## OUTPUT ##################
