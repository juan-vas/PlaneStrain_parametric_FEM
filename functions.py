import sys
import numpy as np
import matplotlib.pyplot as plt




############# FUNCTIONS ##############

def check_input_validity(number_of_plies, ply_index, defect_width, defect_type : int):
    if not isinstance(number_of_plies, int):
        print("Unvalid Input: Number of plies needs to be an integer")
        sys.exit()
    
    if not number_of_plies > 1:
        print("Unvalid Input: Number of plies needs to be greater than one")
        sys.exit()

    if not isinstance(ply_index, int):
        print("Unvalid Input: Ply index needs to be an integer")
        sys.exit()

    if not ((ply_index > 1) and (ply_index < number_of_plies)):
        print("Unvalid Input: The index of the ply with the defect must be " \
        "greater than 1 and less than the total number of plies")
        sys.exit()

    if not (defect_width < 5.0 and defect_width > 0.0):
        print("Unvalid Input: Defect width needs to be 0 < x < 5 mm")
        sys.exit()

    if not ((defect_type == 0) or (defect_type == 1)):
        print("Unvalid Input: Unvalid defect type code")
        sys.exit()
    
    print("Inputs are valid")

def get_max_ondulation(x, gap_width):
    beta = 0.08
    amplitude = gap_width * beta

    laminate_width = np.max(x)
    laminate_center = laminate_width / 2
    limit_left = laminate_center - gap_width / 2
    limit_right = laminate_center + gap_width / 2
    y = x
    y = np.where((y > limit_left) & (y < limit_right),
                  0.5 * (1 + np.cos(np.pi * (y - laminate_center) / (gap_width/2) ))
                  , 0)
    result = y * amplitude
    return result

def apply_ondulation(y, flawed_ply, defect_index):
    alpha = 0.55
    counter = defect_index
    while counter < np.size(y,0):
        a = y[counter]
        b = a - flawed_ply * np.exp(-alpha * (counter - defect_index))
        y[counter] = b
        counter += 1
    return y

def plot_geometry(x, y, x_left = None, y_left = None, x_right = None, y_right = None):
    
    fig, ax = plt.subplots()

    i = 0
    while i < y.shape[0]:
        ax.plot(x, y[i], color='k')
        i += 1

    ax.plot([0, 0], [np.min(y), np.max(y)], color='k')
    ax.plot([np.max(x), np.max(x)], [np.min(y), np.max(y)], color='k')

    if x_left is not None:
        ax.plot(x_left, y_left, color = 'k')
        ax.plot(x_right, y_right, color = "k")

    ax.set_ylim(-0.1 * np.max(y), 1.1 * np.max(y))
    ax.set_aspect('equal', adjustable='datalim')

    ax.set_title('xxx')
    ax.set_xlabel('x [mm]')
    ax.set_ylabel('y [mm]')
    plt.show()