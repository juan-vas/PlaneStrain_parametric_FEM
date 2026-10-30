from pathlib import Path
import pandas as pd
import numpy as np
from create_material.interfaces import Material
import copy

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
        property_sequence.append(counter + 100)
        counter += 1
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
    case_control_collection.append('SUBCASE = 1\n')
    case_control_collection.append('    LABEL loadstep1\n')
    case_control_collection.append('    ANALYSIS STATICS\n')
    case_control_collection.append('    SPC = %d\n'%(SID_SPC))
    case_control_collection.append('    LOAD = %d\n'%(SID_SPCD))
    case_control_collection.append('    DISPLACEMENT (OPTI) = ALL\n')
    case_control_collection.append('    STRESS (OPTI) = YES\n')
    case_control_collection.append('    SPCF (OPTI) = 900103\n')
    case_control_collection.append('\n')
    case_control_collection.append('BEGIN BULK\n')
    return case_control_collection

def prepare_nastran_materials(material_index : pd.DataFrame):
    material_collection = []
    bdf_line_1 = material_index['material_line_1'].tolist()
    bdf_line_2 = material_index['material_line_2'].tolist()
    i = 0
    while i < len(bdf_line_1):
        material_collection.append(bdf_line_1[i])
        material_collection.append(bdf_line_2[i])
        i += 1
    return material_collection

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

def update_material(material : Material, element_index : pd.DataFrame, 
                    ply_index : pd.DataFrame, material_index : pd.DataFrame,
                    property_index : pd.DataFrame, ply_thickness
                    ):
    fvf_original = material.fvf
    df_orientations = ply_index[['fiber_angle', 'pid']]
    element_index = pd.merge(
        left= element_index,
        right= df_orientations,
        how= 'inner',
        on= 'pid'
    )

    pid = 201 # Property code for modified property
    mid = 2001
    for row in element_index.itertuples():
        if (element_index.loc[row[0], 'fvf'] < fvf_original) & (int(element_index.loc[row[0], 'pid']) < 200):
            new_fvf = element_index.loc[row[0], 'fvf']
            fiber_angle = int(element_index.loc[row[0], 'fiber_angle'])
            new_material = copy.copy(material)
            new_material.modify_by_fvf(new_fvf)
            new_material.mid = mid
            new_material.get_rotated_ply(fiber_angle, ply_thickness, material_index)
            new_property_name = f"PLY_{fiber_angle:02d}_deg FVF_{new_fvf}"
            new_property = [pid, new_property_name, new_material.mid, ply_thickness]
            property_index.loc[len(property_index)] = new_property
            element_index.loc[element_index[(element_index['fvf'] == new_fvf) & (element_index['fiber_angle']==fiber_angle)].index, 'pid'] = pid
            pid += 1
            mid += 1
    return element_index

def prepare_pshell(property_index: pd.DataFrame):
    pshell_collection = []
    for row in property_index.itertuples():
        entry_1 = f"PSHELL,{row.pid},{row.mid},{row.shell_thickness}"
        entry_2 = f'$HMNAME PROP {row.pid} "{row.name}"'
        pshell_collection.append(entry_1)
        pshell_collection.append(entry_2)
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
        entry = "GRID,%d,0,%.7f,%.7f,0.0,0"%(row.node_id, row.x, row.y)
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
            set_collection.append(d)
            d = '+,'
        i += 1
    set_collection.append(d)
    return set_collection

def prepare_loaddef():
    loaddef_collection = ['LOADDEF,900040,SPCD,900040']
    return loaddef_collection

def prepare_spc(spc_id, set_id, constraint, displacement):
    spc_collection = []
    if displacement != 0.0:
        entry = 'SPCD,%d,%d,%d,%.6g'%(spc_id, set_id, constraint, displacement)
    else:
        entry = 'SPC,%d,%d,%d,0.0'%(spc_id, set_id, constraint)
    spc_collection.append(entry)
    spc_collection.append('+,GSET')
    return spc_collection

def create_element_index(curve_a : pd.DataFrame, curve_b : pd.DataFrame, element_index : pd.DataFrame, pid : int, ply_thickness, fvf_0):
    element_id = len(element_index) + 1
    number_of_nodes_per_curve = curve_a.shape[0]
    counter = 0
    while counter < number_of_nodes_per_curve - 1:
        a = curve_a.loc[counter, 'node_id']
        b = curve_a.loc[counter + 1, 'node_id']
        c = curve_b.loc[counter + 1, 'node_id']
        d = curve_b.loc[counter, 'node_id']

        # Calculate local thickness 
        y_a = float(curve_a.loc[counter, 'y'])
        y_b = float(curve_a.loc[counter + 1, 'y'])
        y_c = float(curve_b.loc[counter + 1, 'y'])
        y_d = float(curve_b.loc[counter, 'y'])

        local_thickness = ( (y_d - y_a) + (y_c - y_b) ) / 2
        
        # Calculate local fiber volume fraction
        fvf = fvf_0 * ply_thickness / 3 / local_thickness
        fvf = round(fvf, 3)

        db_entry = [element_id, pid, a, b, c, d, fvf]
        element_index.loc[len(element_index)] = db_entry

        element_id += 1
        counter += 1

def prepare_cquad4(element_index : pd.DataFrame):
    cquad_collection = []
    for row in element_index.itertuples():
        entry = f"CQUAD4,{row.element_id},{row.pid},{row.node_a},{row.node_b},{row.node_c},{row.node_d}"
        cquad_collection.append(entry)
    return cquad_collection

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
            # Cut down to 7 characters maximum if it is too long
            trimmed = part[:7]
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
        