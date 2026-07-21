import functions as f
import interfaces as i

################ INPUT #################
number_of_plies = 8
ply_with_defect_index = 4
defect_width = 0.6

############### METHOD #################
f.check_input_validity(number_of_plies, ply_with_defect_index, defect_width)
pristine_laminate = i.Laminate(number_of_plies)
flawed_laminate = i.apply_defect(pristine_laminate, defect_width, ply_with_defect_index)
i.plot_geometry(flawed_laminate)