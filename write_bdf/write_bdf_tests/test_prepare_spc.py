############### INPUT #################
spc_id = 900099
set_id = 900100
constraint = 3
displacement = 0.0

############### METHOD ################
def prepare_spc(spc_id, set_id, constraint, displacement):
    spc_collection = []
    if displacement != 0.0:
        entry = 'SPCD,%d,%d,%d,%.6g'%(spc_id, set_id, constraint, displacement)
    else:
        entry = 'SPC,%d,%d,%d,0.0'%(spc_id, set_id, constraint)
    spc_collection.append(entry)
    spc_collection.append('+,GSET')
    return spc_collection

############### OUTPUT ################
result = prepare_spc(spc_id, set_id, constraint, displacement)
print(result)
