import matplotlib.pyplot as plt
import numpy as np

############## INPUT #############
x = np.linspace(0,5,6)
y = np.array([[0, 1, 2, 3]])
y = np.repeat(y, 6, axis=0)
y = np.transpose(y)


############# METHOD #################

def plot_geometry(x, y):
    
    fig, ax = plt.subplots()

    i = 0
    while i < y.shape[0]:
        ax.plot(x, y[i], color='k')
        i += 1

    ax.plot([0, 0], [np.min(y), np.max(y)], color='k')
    ax.plot([np.max(x), np.max(x)], [np.min(y), np.max(y)], color='k')
    ax.set_ylim(-0.1 * np.max(y), 1.1 * np.max(y))
    ax.set_aspect('equal', adjustable='box')

    ax.set_title('xxx')
    ax.set_xlabel('x [mm]')
    ax.set_ylabel('y [mm]')
    plt.show()

############# OUTPUT ##################

plot_geometry(x,y)