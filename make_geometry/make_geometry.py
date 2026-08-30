from make_geometry import functions as f
from make_geometry import interfaces as i

################ INPUT #################
number_of_plies = 8
ply_with_defect_index = 4
defect_width = 0.5
# Defect Type
## Ondulation   : 0
## Gap          : 1
defect_type = 0

############### METHOD #################
def make_geometry(target_directory, number_of_plies, ply_with_defect_index, defect_width, defect_type):
    f.check_input_validity(number_of_plies, ply_with_defect_index, defect_width, defect_type)
    defect = i.create_defect(ply_with_defect_index, defect_width, defect_type)
    laminate = i.Laminate(number_of_plies, defect)
    flawed_laminate = i.apply_ondulation(laminate, defect)
    if defect.defect_type == 1: i.apply_gap(flawed_laminate, defect)
    ax = i.plot_geometry(flawed_laminate, target_directory)
    i.create_auxiliary_curves(flawed_laminate, target_directory, ax)
    i.write_bdf(flawed_laminate, target_directory= target_directory)