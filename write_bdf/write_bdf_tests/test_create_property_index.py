import pandas as pd

##### INPUT #######
laminate_sequence = [45, -45, 0, 90, 90, 0, -45, 45, 0, -45, 45]
ply_thickness = 0.25
defect_type = 1

#### METHOD #####''
def create_property_index(laminate_sequence : list, ply_thickness: float, defect_type: int):
    property_index = pd.DataFrame(columns=['pid', 'name', 'mid', 'shell_thickness'])
    materal_sequence = []
    if defect_type == 1:
        new_property = [1, 'GAP_RESIN', 1, ply_thickness]
        property_index.loc[len(property_index)] = new_property
    for ply in laminate_sequence:
        match ply:
            case 0:
                materal_sequence.append(1001)
            case 45:
                materal_sequence.append(1002)
            case -45:
                materal_sequence.append(1003)
            case 90:
                materal_sequence.append(1004)

    counter = 1
    for ply in laminate_sequence:
        new_property = [counter + 100, f"PLY_{counter:02d}", materal_sequence[counter - 1], ply_thickness]
        property_index.loc[len(property_index)] = new_property
        counter += 1
    return property_index

####### OUTPUT #######
result = create_property_index(laminate_sequence, ply_thickness, defect_type)
print(result)
    
        