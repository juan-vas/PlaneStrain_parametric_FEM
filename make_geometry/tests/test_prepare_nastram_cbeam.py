################## INPUT #################
new_x = [2.0, 1.0, 2.0]
new_y = [3.3, 4.023, 9.342]
c_beam_collection = ['as', 'as']
node_count = 10

################## METHOD #################
def prepare_nastran_cbeam(new_x : list, collection : list, node_count : int):
    eid = len(collection) + 1
    node_id = node_count 
    for element in new_x[:-1]:
        entry = "CBEAM,%d,1,%d,%d,0,0,1"%(eid, node_id + 1, node_id + 2)
        collection.append(entry)
        node_id += 1
        eid += 1
    return collection

################# OUTPUT ####################
result = prepare_nastran_cbeam(new_x=new_x, collection= c_beam_collection, node_count= 10)
print(result)