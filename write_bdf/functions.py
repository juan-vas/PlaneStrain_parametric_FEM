### Functions of the write_bdf package ###


def prepare_nastran_material(mid, e_modulus, g_modulus, nu, rho):
    material_collection = []
    entry = "MAT1,%d,%.10g,%.10g,%.10g,%.10g"%(mid, e_modulus, g_modulus, nu, rho)
    material_collection.append(entry)
    return material_collection

def prepare_nastran_pbeam(mid, area, inertia_1, inertia_2, torsional_constant_J):
    format_check = [area, inertia_1, inertia_2, torsional_constant_J]
    entry = "PBEAM,1,%d"%(mid)
    for element in format_check:
        check = ",%.10g"%(element)
        if len(check) > 8:
            check = ",%.4g"%(element)
            check = check.replace("e", "")

        if check[-3:-1] == "-0":
            check = ",%.5g"%(element)
            check = check.replace("e-0", "-")

        entry = entry + check

    pbeam_collection = []
    pbeam_collection.append(entry)
    return pbeam_collection

def prepare_nastran_grid(new_x : list, new_y : list, grid_collection : list):
    id = len(grid_collection) + 1
    i = 0
    for element in new_x:
        entry = "GRID,%d,0,%.10g,%.10g,0.0"%(id, new_x[i], new_y[i])
        grid_collection.append(entry)
        id += 1
        i += 1

    return grid_collection

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
    with open(filename, "w", encoding="utf-8") as file:
        file.writelines(collection)