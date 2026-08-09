############### INPUT ###########
mid = 1
area = 0.01
i1 = 8.333333333e-6
i2 = 8.33333333333333e-6
j_torsion = 6.66666667e-5

########## METHOD ###########
def prepare_nastran_pbeam(mid, area, inertia_1, inertia_2, torsional_constant_J):
    format_check = [area, inertia_1, inertia_2, torsional_constant_J]
    entry = "PBEAM,1"
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

####################### OUTPUT ###########################
result = prepare_nastran_pbeam(mid, area, i1, i2, j_torsion)
print(result)