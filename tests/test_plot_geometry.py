import matplotlib.pyplot as plt
import numpy as np

############## INPUT #############
x = np.linspace(0,5,6)
y = np.array([[0, 1, 2, 3]])
y = np.repeat(y, 6, axis=0)
y = np.transpose(y)


############# METHOD #################

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

    ax.set_title('xxx')
    ax.set_xlabel('x [mm]')
    ax.set_ylabel('y [mm]')
    # plt.show()
    return fig, ax

############# OUTPUT ##################

fig, ax = plot_geometry(x,y)
plt.show()