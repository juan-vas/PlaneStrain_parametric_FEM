from pathlib import Path
import pandas as pd
import numpy as np

### Functions of the write_bdf package ###

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

def prepare_case_control():
    SID_SPC = 900099 # Único set de SPC
    SID_SPCD = 900040 # Set para SPCD (UX borde derecho)
    case_control_collection = []
    case_control_collection.append('$HMNAME LOADSTEP %d "loadstep1"\n'%(1))
    case_control_collection.append('\n')
    case_control_collection.append('SUBCASE 1\n')
    case_control_collection.append('    LABEL loadstep1\n')
    case_control_collection.append('    ANALYSIS STATICS\n')
    case_control_collection.append('    SPC = %d\n'%(SID_SPC))
    case_control_collection.append('    LOAD = %d\n'%(SID_SPCD))
    case_control_collection.append('    DISPLACEMENT = ALL\n')
    case_control_collection.append('    STRESS = YES\n')
    case_control_collection.append('    SPCF = ALL\n')
    case_control_collection.append('\n')
    case_control_collection.append('BEGIN BULK\n')
    return case_control_collection

def prepare_nastran_material():
    material_collection = []
    material_collection.append('MAT1, 1, %.9g, , %.9g\n'%(4660, 0.35))
    material_collection.append('$HNAME MAT 1 "RESIN_8552_2D"')

    material_collection.append('$ === UD 8552/AS4 (RTD, seco) | MAT8 por orientación ===')
    material_collection.append('MAT8,1001,127300,9240,0.302,4830.0,4830.0,3600.0,1.6e-09')
    material_collection.append('+ , , , , , , , ,1996.0,1398.0,63.9,268.0,74.0')
    material_collection.append('$HMNAME MAT 1001 "UD_8552_AS4_0deg"')
    material_collection.append('MAT8,1002,12563.8,12563.8,0.3006,6100.1,4830.0,3600.0,1.6e-09')
    material_collection.append('+ , , , , , , , ,1996.0,1398.0,63.9,268.0,74.0')
    material_collection.append('$HMNAME MAT 1002 "UD_8552_AS4_+45deg"')
    material_collection.append('MAT8,1003,12563.8,12563.8,0.3006,6100.1,4830.0,3600.0,1.6e-09')
    material_collection.append('+ , , , , , , , ,1996.0,1398.0,63.9,268.0,74.0')
    material_collection.append('$HMNAME MAT 1003 "UD_8552_AS4_-45deg"')
    material_collection.append('MAT8,1004,9240.0,127300.0,0.0219205,4830.0,4830.0,3600.0,1.6e-09')
    material_collection.append('+ , , , , , , , ,1996.0,1398.0,63.9,268.0,74.0')
    material_collection.append('$HMNAME MAT 1004 "UD_8552_AS4_90deg"')
    return material_collection

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

def prepare_node_index(new_x : list, new_y : list, node_index : list, curve_id : int, is_boundary : bool):
    id = len(node_index) + 1
    i = 0
    for element in new_x:
        entry = [id, new_x[i], new_y[i], curve_id, is_boundary]
        node_index.append(entry)
        id += 1
        i += 1
    return node_index

def prepare_grid(node_index : pd.DataFrame):
    grid_collection = []
    for row in node_index.itertuples():
        entry = "GRID,%d,0,%.10g,%.10g,0.0"%(row.node_id, row.x, row.y)
        grid_collection.append(entry)
    return grid_collection

def prepare_set(node_index : pd.DataFrame, set_id: list):
    set_number = set_id[0]
    set_label = set_id[1]
    set_collection = []
    a = f'$HMSET {set_number} 1 "{set_label}" 18'
    b = '$HMSETTYPE 1 "non-ordered" 18'
    c = f'SET,{set_number},GRID,LIST'
    set_collection.append(a)
    set_collection.append(b)
    set_collection.append(c)
    number_of_nodes = len(node_index)
    d = '+,'
    i = 0
    for row in node_index.itertuples():
        d = d + '%d,'%(row.node_id) 
        if (i + 1) % 8 == 0:
            d = d + '\n+,'
        i += 1
    set_collection.append(d)
    return set_collection

def prepare_spc(spc_id, set_id, constraint, displacement):
    spc_collection = []
    if displacement != 0.0:
        entry = 'SPCD,%d,%d,%d,%.6g\n+,GSET'%(spc_id, set_id, constraint, displacement)
    else:
        entry = 'SPC,%d,%d,%d,0.0\n+,GSET'%(spc_id, set_id, constraint)
    spc_collection.append(entry)
    return spc_collection

def prepare_cquad4(curve_a : pd.DataFrame, curve_b : pd.DataFrame, cquad_collection : list, pid : int):
    element_id = len(cquad_collection) + 1
    number_of_nodes_per_curve = curve_a.shape[0]
    counter = 0
    while counter < number_of_nodes_per_curve - 1:
        a = curve_a.loc[counter, 'node_id']
        b = curve_a.loc[counter + 1, 'node_id']
        c = curve_b.loc[counter + 1, 'node_id']
        d = curve_b.loc[counter, 'node_id']
        entry = 'CQUAD4,%d,%d,%d,%d,%d,%d'%(element_id, pid, a, b, c, d)
        element_id += 1
        counter += 1
        cquad_collection.append(entry)
    return cquad_collection

def prepare_nastran_cbeam(new_x : list, collection : list, node_count : int):
    eid = len(collection) + 1
    node_id = node_count 
    for element in new_x[:-1]:
        entry = "CBEAM,%d,1,%d,%d,0,0,1"%(eid, node_id + 1, node_id + 2)
        collection.append(entry)
        node_id += 1
        eid += 1
    return collection

def format_nastran_line(collection: list) -> list:
    formatted_lines = []
    for element in collection:
        if element.startswith("$"): 
            formatted_lines.append(element + "\n")
            continue
    # Split exactly by commas
        parts = element.split(",")
        
        formatted_parts = []
        for part in parts:
            # Cut down to 8 characters maximum if it is too long
            trimmed = part[:8]
            # Pad with trailing spaces to ensure it is exactly 8 characters wide
            padded = trimmed.ljust(8)
            formatted_parts.append(padded)
            
        # Join everything back together with zero spaces or commas between fields
        formatted_line = "".join(formatted_parts) + "\n"
        formatted_lines.append(formatted_line) 
    return formatted_lines

def write_bdf(filename, collection):
    file_path = Path(filename)
    if file_path.exists():
        with open(filename, "a", encoding="utf-8") as file:
            file.writelines(collection)
    else:
        with open(filename, "w", encoding="utf-8") as file:
            file.writelines(collection)
        