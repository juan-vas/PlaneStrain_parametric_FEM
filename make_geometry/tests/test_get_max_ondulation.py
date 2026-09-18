import numpy as np
import matplotlib.pyplot as plt

############# INPUT #############
n = 100
laminate_width = 5.0
x = np.linspace(0, laminate_width, n)
y = np.ones(n)
gap_width = 2.2
ply_thickness = 0.125

# result = y
# print(result)
# plt.plot(x, y)
# plt.show()

############# METHOD #############
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
    


############# OUTPUT #############
if __name__ == "__main__":
    y = get_max_ondulation(x, gap_width)
    # result = max(y)
    result = y
    print(result)
