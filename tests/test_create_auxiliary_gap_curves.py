import numpy as np
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
######################### INPUT ##########################
x = np.linspace(0,5,6)
y = np.array([[0.0, 1.0, 2.0, 3.0, 4.0]])
y = np.repeat(y, 6, axis=0)
y = np.transpose(y)

fig, ax = plt.subplots()
ax.plot(x,y[0])

ply_with_defect_index = 1
ply_thickness = 1
x_intersection_left = 1.5
x_intersection_right = 2.5

######################### METHOD ##############################
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

########################## OUTPUT #############################
create_auxiliary_gap_curves(ax, x, ply_with_defect_index, ply_thickness, x_intersection_left, x_intersection_right)
plt.show()