import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.axes import Axes

############# FUNCTIONS: GEOMETRY ##############
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

    if not (defect_width < 5.0 and defect_width >= 0.0):
        print("Unvalid Input: Defect width needs to be 0 < x < 5 mm")
        sys.exit()

    if not ((defect_type == 0) or (defect_type == 1)):
        print("Unvalid Input: Unvalid defect type code")
        sys.exit()
    
    print("Inputs are valid")

def get_max_ondulation(x, gap_width):
    beta = 0.05
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
    linewidth = 1.0

    i = 0
    while i < y.shape[0]:
        ax.plot(x, y[i], color='k', lw = linewidth)
        i += 1

    ax.plot([0, 0], [np.min(y), np.max(y)], color='k', lw = linewidth)
    ax.plot([np.max(x), np.max(x)], [np.min(y), np.max(y)], color='k', lw = linewidth)

    if x_left is not None:
        ax.plot(x_left, y_left, color = 'k', lw = linewidth)
        ax.plot(x_right, y_right, color = "k", lw = linewidth)

    ax.set_ylim(-0.1 * np.max(y), 1.1 * np.max(y))
    ax.set_aspect('equal', adjustable='datalim')

    # ax.set_title('xxx')
    ax.set_xlabel('x [mm]')
    ax.set_ylabel('y [mm]')
    # plt.show()
    return fig, ax

def create_internal_auxiliary_curves(x, y):
    counter = 0
    number_of_curves = y.shape[0]
    auxiliary_curves = y[0]
    while counter < number_of_curves - 1:
        a = y[counter + 1] - y[counter]
        b = y[counter] + a * 1/3
        c = y[counter] + a * 2/3
        auxiliary_curves = np.concatenate((auxiliary_curves, b,c))
        counter += 1
    num_rows = 2 * number_of_curves - 1
    num_columns = y.shape[1]
    auxiliary_curves = auxiliary_curves.reshape(num_rows,num_columns)
    auxiliary_curves = np.delete(auxiliary_curves, 0, axis= 0)
    return auxiliary_curves

def plot_auxiliary_curves(x, y_auxiliary, ax):
    counter = 0
    linewidth = 0.3
    while counter < y_auxiliary.shape[0]:
        ax.plot(x, y_auxiliary[counter], color = "k", lw = linewidth)
        counter += 1

def create_auxiliary_gap_curves(ax: Axes, x, ply_with_defect_index, ply_thickness, x_intersection_left, x_intersection_right):
    height_base = (ply_with_defect_index - 1) * ply_thickness
    height_1 = height_base + ply_thickness * 1/4
    height_2 = height_base + ply_thickness * 2/3
    x_left = x[(x < x_intersection_left)]
    x_right = x[(x > x_intersection_right)]
    y1_left = np.ones(np.size(x_left)) * height_1
    y1_right = np.ones(np.size(x_right)) * height_1
    y2_left = np.ones(np.size(x_left)) * height_2
    y2_right = np.ones(np.size(x_right)) * height_2
    ax.plot(x_left, y1_left, color = "k", linewidth = 0.3)
    ax.plot(x_right, y1_right, color = "k", linewidth = 0.3)
    ax.plot(x_left, y2_left, color = "k", linewidth = 0.3)
    ax.plot(x_right, y2_right, color = "k", linewidth = 0.3)

def plot_line_between_bezier(ax, x_left : np.ndarray, y_left : np.ndarray, x_right : np.ndarray, y_right :np.ndarray):
    index_point_1 = np.argmax(x_left)
    index_point_2 = np.argmin(x_right)
    x_point_1 = x_left[index_point_1]
    y_point_1 = y_left[index_point_1]
    x_point_2 = x_right[index_point_2]
    y_point_2 = y_right[index_point_2]
    ax.plot([x_point_1, x_point_2], [y_point_1, y_point_2], color = "k", linewidth = 0.3)

