import create_directory as cd
import choose_laminate as cl
from make_geometry.make_geometry import make_geometry 
from make_geometry.interfaces import Laminate
from write_bdf.write_bdf import write_bdf
import run_optistruct as ro

################ INPUT #################
workspace = r"C:\Users\juanv\Documents\Work\01 Politecnico de Madrid\99 TFM\05 Virtual Experiments\\"
optistruct_exec = r'C:\Program Files\Altair\2026.1\hwsolvers\scripts\optistruct.bat'

# 1) QI-8   : [45/0/-45/90]s
# 2) QI-16  : [45/0/-45/90/0/-45/0/45]s
# 3) ±45 sesgado (14): [45/0/-45/90/45/0/-45]s
# 4) 0° dominante (14): [0/45/-45/0/90/0/45]s
# 5) 90° reforzado (16): [45/0/90/0/-45/0/90/0]s
# 6) Spread-tow (16): [45/0/-45/90/-45/0/45/90]s
laminate_choice = 1

ply_with_defect_index = 4
defect_width = 0.1
# Defect Type
## Ondulation   : 0
## Gap          : 1
defect_type = 0

############### METHOD #################
experiment_label = "Laminate_%02d_Defect_%d_at_%02d_w_%.2f"%(laminate_choice, defect_type, ply_with_defect_index, defect_width)
target_directory = cd.create_directory(workspace, experiment_label)
laminate_sequence = cl.choose_laminate(laminate_choice)
number_of_plies = len(laminate_sequence)
flawed_laminate = make_geometry(target_directory, number_of_plies, ply_with_defect_index, defect_width, defect_type)
filename = write_bdf(flawed_laminate, target_directory, laminate_sequence)
ro.run_optistruct_analysis(bdf_file_path= filename,
                           output_dir= target_directory,
                           optistruct_exec= optistruct_exec)

############# OUTPUT ################
print(experiment_label)
