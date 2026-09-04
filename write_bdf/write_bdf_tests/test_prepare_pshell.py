############ INPUT ###################
laminate_sequence = [45, -45, 0, 90, 90, 0, -45, 45, 0, -45, 45]
ply_thickness = 0.25
defect_type = 1

############ METHOD ##################
def prepare_pshell(laminate_sequence : list, ply_thickness : float, defect_type = int):
    pshell_collection = []
    materal_sequence = []

    if defect_type == 1:
        pshell_collection.append('PSHELL,2,1,%.6g'%(ply_thickness))
        pshell_collection.append('$HMNAME PROP 2 "GAP_RESIN_2D"')
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
        entry_1 = 'PSHELL,%d,%d,%.6g'%(counter + 100, materal_sequence[counter - 1] ,ply_thickness)
        entry_2 = '$HNAME PROP %d "PLY_%02d_2D"'%(counter + 100, counter)
        pshell_collection.append(entry_1)
        pshell_collection.append(entry_2)
        counter += 1
    return pshell_collection

############ OUTPUT ##################
result = prepare_pshell(laminate_sequence, ply_thickness, defect_type)
print(result)
