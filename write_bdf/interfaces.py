from write_bdf import functions as f
from make_geometry.interfaces import Laminate, Gap
import pandas as pd

def create_ply_index(laminate_sequence : list):
    ply_index = f.create_ply_index(laminate_sequence)
    return ply_index

def prepare_case_control():
    case_control_collection = f.prepare_case_control()
    return case_control_collection

def prepare_material():
    material_collection = f.prepare_nastran_material()
    return material_collection

def prepare_pshell(Laminate: Laminate, laminate_sequence : list):
    ply_thickness = Laminate.ply_thickness
    defect = Laminate.defect
    if isinstance(defect, Gap):
        defect_type = 1
    else: defect_type = 0
    pshell_collection = f.prepare_pshell(laminate_sequence, ply_thickness, defect_type)
    return pshell_collection

def prepare_node_index(Laminate: Laminate):
    x = Laminate.x
    y = Laminate.y
    y_auxiliary = Laminate.y_auxiliary
    defect = Laminate.defect
    number_of_plies = Laminate.number_of_plies
    node_index = []
    total_number_of_nodes = 0
    counter = 0
    curve_label = 0
    for elem in y:
        num_nodes_per_curve = len(elem)
        node_index = f.prepare_node_index(x, y[counter], node_index, curve_label, True)
        curve_label += 1

        if counter != number_of_plies:
            node_index = f.prepare_node_index(x, y_auxiliary[2 * counter], node_index, curve_label, False)
            curve_label += 1
            node_index = f.prepare_node_index(x, y_auxiliary[2 * counter + 1], node_index, curve_label, False)
            curve_label += 1
        total_number_of_nodes = total_number_of_nodes + num_nodes_per_curve
        counter +=1

    if isinstance(Laminate.defect, Gap):
        x_left = defect.x_bezier_left
        y_left = defect.y_bezier_left
        x_right = defect.x_bezier_right
        y_right = defect.y_bezier_right

        num_nodes_per_curve = len(x_left)
        node_index = f.prepare_node_index(x_left, y_left, node_index, curve_label, False)
        curve_label += 1
        total_number_of_nodes = total_number_of_nodes + num_nodes_per_curve

        num_nodes_per_curve = len(x_right)
        node_index = f.prepare_node_index(x_right, y_right, node_index, curve_label, False)
        curve_label += 1
        total_number_of_nodes = total_number_of_nodes + num_nodes_per_curve
    node_index = pd.DataFrame(data=node_index,
                              columns=['node_id', 'x', 'y', 'curve_id', 'is_boundary'])

    return node_index

def prepare_grid(node_index : pd.DataFrame):
    grid_collection = f.prepare_grid(node_index)
    return grid_collection

def prepare_set(node_index : pd.DataFrame):
    nodes_all = node_index
    set_id_all = ['900100', 'ALL_NODES']
    set_collection = f.prepare_set(node_index = nodes_all, set_id= set_id_all)

    nodes_left = node_index[node_index['x'] == 0]
    set_id_left = ['900101', "LEFT_EDGE"]
    set_collection_left = f.prepare_set(node_index= nodes_left, set_id= set_id_left)

    nodes_right = node_index[node_index['x'] == node_index['x'].max()]
    set_id_right = ['900103', 'RIGHT_EDGE']
    set_collection_right = f.prepare_set(node_index= nodes_right, set_id= set_id_right)

    nodes_left_bottom = node_index[(node_index['x'] == 0) & (node_index['y'] == 0)]
    set_id_left_bottom = ['900102', 'LEFT_BOTTOM_NODE']
    set_collection_left_bottom = f.prepare_set(node_index= nodes_left_bottom, set_id= set_id_left_bottom)

    set_collection = set_collection + set_collection_left + set_collection_right + set_collection_left_bottom

    return set_collection

def prepare_loaddef():
    loaddef_collection = f.prepare_loaddef()
    return loaddef_collection

def prepare_spc():
    spc_collection_z = f.prepare_spc(900099, 900100, 3, 0.0)
    spc_collection_x_left = f.prepare_spc(900099, 900101,1, 0.0)
    spc_collection_y = f.prepare_spc(900099, 900102, 2, 0.0)
    spc_collection_x_right = f.prepare_spc(900099,900103, 1, 0.0)
    spc_collection_disp = f.prepare_spc(900040, 900103, 1, 0.12)
    spc_collection = spc_collection_z + spc_collection_x_left + spc_collection_y + spc_collection_x_right + spc_collection_disp
    return spc_collection

def prepare_cquad4(node_index : pd.DataFrame, ply_index : pd.DataFrame):
    cquad_collection = []
    number_of_curves = node_index['curve_id'].max()
    counter = 0
    while counter < number_of_curves:
        curve_a = node_index[node_index['curve_id'] == counter].reset_index(drop= True)
        curve_b = node_index[node_index['curve_id'] == counter + 1].reset_index(drop= True)
        bottom_curve_id = curve_a.loc[0,'curve_id']
        if curve_a.loc[0,'is_boundary'] == True:
            corresponding_ply_id = ply_index[ply_index['bottom_curve_id'] == bottom_curve_id].reset_index(drop= True)
            pid = corresponding_ply_id.loc[0,'pid']
        cquad_collection = f.prepare_cquad4(curve_a, curve_b, cquad_collection, pid)
        counter += 1
    return cquad_collection

def format_nastran_line(collection):
    collection = f.format_nastran_line(collection)
    return collection

def write_bdf(filename, collection):
    f.write_bdf(filename, collection)
