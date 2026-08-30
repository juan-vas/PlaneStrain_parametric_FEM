from make_geometry.interfaces import Laminate
import interfaces as i

def write_bdf(Laminate: Laminate, target_directory):
    filename = target_directory + r"\input_analysis.bdf"

    material_collection = i.prepare_material(Laminate)
    pbam_collection = i.prepare_pbeam(Laminate)
    cbeam_collection, grid_collection = i.prepare_grid(Laminate)
    collection = material_collection + pbam_collection + grid_collection + cbeam_collection
    collection = i.format_nastran_line(collection)
    i.write_bdf(filename, collection)
    print("The .bdf file has been successfully created in " + filename)