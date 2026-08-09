import matplotlib.pyplot as plt
import numpy as np

############# INPUT ###############
x = np.linspace(0,5,6)
y = x ** 2
y_aux = x ** 2 + 1
y_aux = np.concatenate((y, y_aux))
y_aux = y_aux.reshape(2, 6)
fig, ax = plt.subplots()
ax.plot(x, y)

############' METHOD ################
def plot_auxiliary_curves(x, y_auxiliary, ax):
    counter = 0
    linewidth = 0.3
    while counter < y_auxiliary.shape[0]:
        ax.plot(x, y_auxiliary[counter], color = "k", lw = linewidth)
        counter += 1

########### OUTPUT ################'
plot_auxiliary_curves(x, y_aux, ax)
plt.show()
