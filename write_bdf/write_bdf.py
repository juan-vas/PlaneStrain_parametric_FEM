from make_geometry.interfaces import Laminate
from write_bdf import interfaces as i

def write_bdf(Laminate: Laminate, target_directory, laminate_sequence : list):
    filename = target_directory + r"\input_analysis.bdf"
    
    ply_index = i.create_ply_index(laminate_sequence)
    case_control_collection = i.prepare_case_control()
    i.write_bdf(filename, case_control_collection)
    material_collection = i.prepare_material()
    pshell_collection = i.prepare_pshell(Laminate, laminate_sequence)
    node_index = i.prepare_node_index(Laminate)
    grid_collection = i.prepare_grid(node_index)
    set_collection = i.prepare_set(node_index)
    loaddef_collection = i.prepare_loaddef()
    spc_collection = i.prepare_spc()
    cquad_collection = i.prepare_cquad4(node_index, ply_index)
    collection = material_collection + pshell_collection + grid_collection + set_collection + loaddef_collection + spc_collection + cquad_collection
    collection = i.format_nastran_line(collection)
    i.write_bdf(filename, collection)
    print("The .bdf file has been successfully created in " + filename)
    return filename

