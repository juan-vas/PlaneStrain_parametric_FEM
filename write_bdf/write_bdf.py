from make_geometry.interfaces import Laminate
from create_material.interfaces import Material
from write_bdf import interfaces as i
import pandas as pd

def write_bdf(Laminate: Laminate, target_directory, laminate_sequence : list, material : Material):
    filename = target_directory + r"\input_analysis.bdf"

    ply_index = i.create_ply_index(laminate_sequence)
    case_control_collection = i.prepare_case_control()
    i.write_bdf(filename, case_control_collection)
    property_index = i.create_property_index(laminate_sequence, Laminate)
    material_index = pd.read_csv("material_db.csv")
    node_index = i.prepare_node_index(Laminate)
    element_index = i.create_element_index(node_index, ply_index, Laminate, material.fvf)
    element_index = i.update_material(material, element_index, ply_index,
                                      material_index, property_index,Laminate.ply_thickness)
    material_collection = i.prepare_material(material_index)
    pshell_collection = i.prepare_pshell(property_index)
    grid_collection = i.prepare_grid(node_index)
    set_collection = i.prepare_set(node_index)
    loaddef_collection = i.prepare_loaddef()
    spc_collection = i.prepare_spc()
    cquad_collection = i.prepare_cquad4(element_index)
    collection = material_collection + pshell_collection + grid_collection + set_collection + loaddef_collection + spc_collection + cquad_collection
    collection = i.format_nastran_line(collection)
    i.write_bdf(filename, collection)
    print("The .bdf file has been successfully created in " + filename)
    return filename

