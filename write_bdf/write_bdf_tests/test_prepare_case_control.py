########## INPUT ############


########## METHOD ############
def prepare_case_control():
    SID_SPC = 900099 # Único set de SPC
    SID_SPCD = 900040 # Set para SPCD (UX borde derecho)
    case_control_collection = []
    case_control_collection.append('$HMNAME LOADSTEP %d "loadstep1"\n'%(1))
    case_control_collection.append('\n')
    case_control_collection.append('SUBCASE 1\n')
    case_control_collection.append('    LABEL loadstep1\n')
    case_control_collection.append('    ANALYSIS STATICS\n')
    case_control_collection.append('    SPC = %d\n'%(SID_SPC))
    case_control_collection.append('    LOAD = %d\n'%(SID_SPCD))
    case_control_collection.append('    DISPLACEMENT = ALL\n')
    case_control_collection.append('    STRESS = YES\n')
    case_control_collection.append('    SPCF = ALL\n')
    case_control_collection.append('\n')
    case_control_collection.append('BEGIN BULK\n')
    return case_control_collection

########## OUTPUT ############
result = prepare_case_control()
print(result)
