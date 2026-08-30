import numpy as np

######### INPUT #############
ply_width = 5
number_of_points = 500
defect_width = 0.5

######### METHOD ###########
def waviness_function(ply_width, number_of_points, defect_width):
    beta = 0.08
    alpha = 0.55
    xc = ply_width / 2
    x_left = xc - defect_width / 2
    x_right = xc + defect_width / 2


    x = np.linspace(0, ply_width, number_of_points)
    f = np.zeros(number_of_points)
    idxwin = x[(x > x_left) & (x < x_right)]

    results = idxwin
    print(results)

###### OUTPUT #########
waviness_function(ply_width, number_of_points, defect_width)