import numpy as np
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
##################### INPUT #######################
x1 = np.array([1, 2, 3, 4, 5, 4, 3, 2, 1])
y1 = np.ones(np.size(x1))
x2 = np.array([1, 2, 3, 4, 5, 4, 3, 2, 1]) + 10
y2 = np.ones(np.size(x1))
fig, ax = plt.subplots()

################### METHOD ######################
def plot_line_between_bezier(ax, x_left : np.ndarray, y_left : np.ndarray, x_right : np.ndarray, y_right :np.ndarray):
    index_point_1 = np.argmax(x_left)
    index_point_2 = np.argmin(x_right)
    x_point_1 = x_left[index_point_1]
    y_point_1 = y_left[index_point_1]
    x_point_2 = x_right[index_point_2]
    y_point_2 = y_right[index_point_2]
    ax.plot([x_point_1, x_point_2], [y_point_1, y_point_2], color = "k", linewidth = 0.3)

#################### OUTPUT #####################
plot_line_between_bezier(ax, x1, y1, x2, y2)
plt.show()