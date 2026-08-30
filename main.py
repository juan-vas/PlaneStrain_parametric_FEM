import create_directory as cd
import choose_laminate as cl
from make_geometry.make_geometry import make_geometry 
from make_geometry.interfaces import Laminate
import write_bdf as w
import numpy as np
################ INPUT #################
workspace = r"C:\Users\juanv\Documents\Work\01 Politecnico de Madrid\99 TFM\03 BDF files\file_"

# 1) QI-8   : [45/0/-45/90]s
# 2) QI-16  : [45/0/-45/90/0/-45/0/45]s
# 3) ±45 sesgado (14): [45/0/-45/90/45/0/-45]s
# 4) 0° dominante (14): [0/45/-45/0/90/0/45]s
# 5) 90° reforzado (16): [45/0/90/0/-45/0/90/0]s
# 6) Spread-tow (16): [45/0/-45/90/-45/0/45/90]s
laminate_choice = 1

ply_with_defect_index = 4
defect_width = 0.5
# Defect Type
## Ondulation   : 0
## Gap          : 1
defect_type = 0


############### METHOD #################
target_directory = cd.prepare_directory(workspace)
laminate_sequence = cl.choose_laminate(laminate_choice)
number_of_plies = len(laminate_sequence)
flawed_laminate = make_geometry(target_directory, number_of_plies, ply_with_defect_index, defect_width, defect_type)
w.write_bdf(flawed_laminate, target_directory)