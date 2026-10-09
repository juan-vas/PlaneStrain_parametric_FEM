import numpy as np

###### INPUT ######'
# Solution for 45 degrees:
solution = np.array([[5075,3867,3714],
                     [3867,5075,3714],
                     [3714, 3714, 4120]])
transformed_stiffness_matrix = np.array([[40597,30937,29712],
                                         [30937,40597,29712],
                                         [29712,29712,32958]])
ply_thickness = 0.125

#######' METHOD ##########
def get_a_matrix(transformed_stiffness_matrix: np.array, ply_thickness : float):
    a_matrix = transformed_stiffness_matrix * ply_thickness
    return a_matrix

######## OUTPUT ############
result = get_a_matrix(transformed_stiffness_matrix, ply_thickness)
np.testing.assert_allclose(result, solution, atol=0.5)
print("✅ Test passed! The function is correctly setup.")