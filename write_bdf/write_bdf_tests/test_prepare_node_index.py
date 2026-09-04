



def prepare_node_index(new_x : list, new_y : list, node_index : list, curve_id : int, is_boundary : bool):
    id = len(node_index) + 1
    i = 0
    for element in new_x:
        entry = [id, new_x[i], new_y[i], curve_id, is_boundary]
        node_index.append(entry)
        id += 1
        i += 1
    return node_index