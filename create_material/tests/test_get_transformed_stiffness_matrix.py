import numpy as np
from numpy.linalg import inv

###### INPUT #######
stiffness_matrix = np.array([[128148, 2809,0],
                    [2809, 9302, 0],
                    [0, 0, 4830]])

# For 90°:
transformation_matrix_90 = np.array([[0,1,0],
                                  [1,0,0],
                                  [0,0,-1]])


solution_90 = np.array([[9302,2809,0],
                     [2809,128148,0],
                     [0,0,4830]])
# For 45°
transformation_matrix_45 = np.array([[0.5,0.5,1],
                                  [0.5,0.5,-1],
                                  [-0.5,0.5,0]])

solution_45 = np.array([[40597,30937,29712],
                     [30937,40597,29712],
                     [29712,29712,32958]])

###### METHOD #######
def get_transformed_stiffness_matrix (transformation_matrix : np.array, stiffness_matrix : np.array):
    q_hat = inv(transformation_matrix) @ stiffness_matrix @ np.transpose(inv(transformation_matrix))
    return q_hat

###### OUTPUT ########
result = get_transformed_stiffness_matrix(transformation_matrix_90, stiffness_matrix)
np.testing.assert_allclose(result, solution_90, atol=0.5)
print("✅ Test 1/2 passed! The function is correctly setup.")

result = get_transformed_stiffness_matrix(transformation_matrix_45, stiffness_matrix)
np.testing.assert_allclose(result, solution_45, atol=0.5)
print("✅ Test 2/2 passed! The function is correctly setup.")
