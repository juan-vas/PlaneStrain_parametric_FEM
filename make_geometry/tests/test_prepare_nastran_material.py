############### INPUT ###########
mid = 1
area = 1
i1 = 1
i2 = 1
j_torsion = 1

########## METHOD ###########
def prepare_nastran_material(mid, e_modulus, g_modulus, nu, rho):
    material_collection = []
    entry = "MAT1,%d,%.10g,%.10g,%.10g,%.10g"%(mid, e_modulus, g_modulus, nu, rho)
    material_collection.append(entry)
    return material_collection

####################### OUTPUT ###########################

result = prepare_nastran_material(mid, area, i1, i2, j_torsion)
print(result)