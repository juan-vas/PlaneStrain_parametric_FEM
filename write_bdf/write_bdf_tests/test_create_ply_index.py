import pandas as pd
import numpy as np

################ INPUT ####################
laminate_sequence = [45, -45, 0, 90, 90, 0, -45, 45, 0, -45, 45]

material_code = [1, 1001, 1002, 1003, 1004]
material_name = ['RESIN_8552_2D', 'UD_8552_AS4_0deg', 'UD_8552_AS4_+45deg', 'UD_8552_AS4_-45deg', 'UD_8552_AS4_90deg']
fiber_angle = [np.nan, 0, 45, -45, 90]
material_inventory = pd.DataFrame({
    'mid': material_code,
    'name': material_name,
    'fiber_angle': fiber_angle
}).astype({'fiber_angle' : 'Int16', 'mid' : 'int'})
print(material_inventory)

###########'### METHOD ####################
def create_ply_index(laminate_sequence):
    ply_id = []
    mid = [1, 1001, 1002, 1003, 1004]
    material_sequence = []
    property_sequence = []
    bottom_curve_sequence = []
    top_curve_sequence = []
    auxiliary_curves_per_ply = 2

    counter = 1
    base_curve = 0
    for ply in laminate_sequence:
        ply_id.append(counter)
        bottom_curve_sequence.append(base_curve)
        top_curve_sequence.append(base_curve + auxiliary_curves_per_ply + 1)
        base_curve = base_curve + auxiliary_curves_per_ply + 1
        counter += 1
        property_sequence.append(counter + 100)
        match ply:
            case 0:
                material_sequence.append(1001)
            case 45:
                material_sequence.append(1002)
            case -45:
                material_sequence.append(1003)
            case 90:
                material_sequence.append(1004)

    ply_index= pd.DataFrame({
        'ply_id' : ply_id,
        'fiber_angle' : laminate_sequence,
        'mid' : material_sequence,
        'pid' : property_sequence,
        'bottom_curve_id' : bottom_curve_sequence,
        'top_curve_id' : top_curve_sequence
    }).astype('Int16')
    return ply_index

################ OUTPUT ###################
if __name__ == "__main__":
    result = create_ply_index(laminate_sequence)
    print(result)