import numpy as np

########## INPUT ##########
e1= 127300
v12=0.302
e2=9240
g12=4830
v21=e2/e1*v12

solution = np.array([[128148, 2809,0],
                    [2809, 9302, 0],
                    [0, 0, 4830]])

######### METHOD #############
def get_stiffness_matrix(E1, v12, v21, E2, G12):
    q11 = E1 / (1 - v12 * v21)
    q22 = E1 * v21 / (1 - v12 * v21)
    q12 = E2 * v12 / (1 - v12 * v21)
    q22 = E2 / (1 - v12 * v21)
    q66 = G12
    stiffness_matrix = np.array([[q11, q12, 0],
                  [q12, q22, 0],
                  [0, 0, q66]])
    return stiffness_matrix

######## OUTPUT #########
result = get_stiffness_matrix(e1, v12,v21,e2,g12)

np.testing.assert_allclose(result, solution, atol=0.5)
print("✅ Test passed! The function is correctly setup.")