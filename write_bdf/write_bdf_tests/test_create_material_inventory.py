import pandas as pd
import numpy as np

#################### INPUT ######################
laminate_sequence = [45, -45, 0, 90, 90, 0, -45, 45, 0, -45, 45]

#################### METHOD ######################
def create_material_inventory():
    material_code = [1, 1001, 1002, 1003, 1004]
    material_name = ['RESIN_8552_2D', 'UD_8552_AS4_0deg', 'UD_8552_AS4_+45deg', 'UD_8552_AS4_-45deg', 'UD_8552_AS4_90deg']
    fiber_angle = [np.nan, 0, 45, -45, 90]
    material_inventory = pd.DataFrame({
        'mid': material_code,
        'name': material_name,
        'fiber_angle': fiber_angle
    }).astype({'fiber_angle' : 'Int16'})
    return material_inventory

#################### OUTPUT ######################
result = create_material_inventory()
print(result)