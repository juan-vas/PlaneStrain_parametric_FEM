import numpy as np
import choose_laminate as cl
from main_batch_version import create_batch

############ INPUT ##############
# 1) QI-8   : [45/0/-45/90]s
# 2) QI-16  : [45/0/-45/90/0/-45/0/45]s
# 3) ±45 sesgado (14): [45/0/-45/90/45/0/-45]s
# 4) 0° dominante (14): [0/45/-45/0/90/0/45]s
# 5) 90° reforzado (16): [45/0/90/0/-45/0/90/0]s
# 6) Spread-tow (16): [45/0/-45/90/-45/0/45/90]s

Laminate = np.arange(1, 7, 1, dtype= int)
Laminate = [int(x) for x in Laminate]
defect_type = 0
defect_width_span = np.arange(0, 2.4, 0.2, dtype= float)

for laminate_choice in Laminate:
    laminate_sequence = cl.choose_laminate(laminate_choice)
    num_of_plies = len(laminate_sequence)
    plies = np.arange(2, num_of_plies, 1, dtype= int)
    plies = [int(x) for x in plies]
    for ply_with_defect_index in plies:
        for defect_width in defect_width_span:
            create_batch(laminate_choice, defect_type, ply_with_defect_index, defect_width)
