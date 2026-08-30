import functions as f
from make_geometry.interfaces import Laminate, Gap

def prepare_material(Laminate: Laminate):
    material = Laminate.material
    mid = material.mid
    E_modulus = material.E_modulus
    G_modulus = material.G_modulus
    nu = material.nu
    rho = material.rho
    material_collection = f.prepare_nastran_material(mid, E_modulus, G_modulus, nu, rho)
    return material_collection

def prepare_pbeam(Laminate: Laminate):
    pbeam = Laminate.pbeam
    mid = pbeam.mid
    area = pbeam.area
    moment_inertia_1 = pbeam.moment_of_inertia_1
    moment_inertia_2 = pbeam.moment_of_inertia_2
    torsional_constant = pbeam.torsional_constant_J
    pbeam_collection = f.prepare_nastran_pbeam(mid, area, moment_inertia_1, moment_inertia_2, torsional_constant)
    return pbeam_collection

def prepare_grid(Laminate: Laminate):
    x = Laminate.x
    y = Laminate.y
    defect = Laminate.defect
    cbeam_collection = []
    grid_collection = []
    total_number_of_nodes = 0
    counter = 0
    for elem in y:
        num_nodes_per_curve = len(elem)
        cbeam_collection = f.prepare_nastran_cbeam(new_x= x, collection= cbeam_collection, node_count= total_number_of_nodes)
        grid_collection = f.prepare_nastran_grid(x, y[counter], grid_collection)
        total_number_of_nodes = total_number_of_nodes + num_nodes_per_curve
        counter +=1

    if isinstance(Laminate.defect, Gap):
        x_left = defect.x_bezier_left
        y_left = defect.y_bezier_left
        x_right = defect.x_bezier_right
        y_right = defect.y_bezier_right

        num_nodes_per_curve = len(x_left)
        cbeam_collection = f.prepare_nastran_cbeam(x_left, cbeam_collection, total_number_of_nodes)
        grid_collection = f.prepare_nastran_grid(x_left, y_left, grid_collection)
        total_number_of_nodes = total_number_of_nodes + num_nodes_per_curve

        num_nodes_per_curve = len(x_right)
        cbeam_collection = f.prepare_nastran_cbeam(x_right, cbeam_collection, total_number_of_nodes)
        grid_collection = f.prepare_nastran_grid(x_right, y_right, grid_collection)
        total_number_of_nodes = total_number_of_nodes + num_nodes_per_curve

    return cbeam_collection, grid_collection

def format_nastran_line(collection):
    collection = f.format_nastran_line(collection)
    return collection

def write_bdf(filename, collection):
    f.write_bdf(filename, collection)
