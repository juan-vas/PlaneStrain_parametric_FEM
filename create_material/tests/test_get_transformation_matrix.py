import numpy as np

####### INPUT ######
solution_90 = np.array([[0,1,0],
                     [1,0,0],
                     [0,0,-1]])

solution_45 = np.array([[0.5,0.5,1],
                     [0.5,0.5,-1],
                     [-0.5,0.5,0]])

###### METHOD #######
def get_transformation_matrix(angle):
    c = np.cos(angle * np.pi / 180)
    s = np.sin(angle * np.pi /180)
    t = np.array([[c**2, s**2, 2 *s*c], 
                  [s**2, c**2, -2*s*c], 
                  [-s*c, s*c, c**2 - s**2]])
    return t

####### OUTPUT #######
# For 90°
result = get_transformation_matrix(90)
np.testing.assert_allclose(result, solution_90, atol= 1e-7)
print("✅ Test 1/2 passed! The function is correctly setup.")

# For 45°
result = get_transformation_matrix(45)
np.testing.assert_allclose(result, solution_45, atol= 1e-7)
print("✅ Test 2/2 passed! The function is correctly setup.")