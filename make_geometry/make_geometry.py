import functions as f
import interfaces as i

################ INPUT #################
number_of_plies = 8
ply_with_defect_index = 4
defect_width = 0.5
# Defect Type
## Ondulation   : 0
## Gap          : 1
defect_type = 1


############### METHOD #################
workspace = r"C:\Users\juanv\Documents\Work\01 Politecnico de Madrid\99 TFM\03 BDF files\file_"

target_directory = i.prepare_directory(workspace)
f.check_input_validity(number_of_plies, ply_with_defect_index, defect_width, defect_type)
defect = i.create_defect(ply_with_defect_index, defect_width, defect_type)
laminate = i.Laminate(number_of_plies, defect)
flawed_laminate = i.apply_ondulation(laminate, defect)
if defect.defect_type == 1: i.apply_gap(flawed_laminate, defect)
ax = i.plot_geometry(flawed_laminate, target_directory)
i.create_auxiliary_curves(flawed_laminate, target_directory, ax)
i.write_bdf(flawed_laminate, target_directory= target_directory)