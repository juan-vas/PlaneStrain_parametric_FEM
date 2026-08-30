import numpy as np

####### INPUT ######
x = np.linspace(0,5,6)
y = np.array([[0.0, 1.0, 2.0, 3.0, 4.0]])
y = np.repeat(y, 6, axis=0)
y = np.transpose(y)
flawed_ply = np.array([0, 0, 0.1, 0.5, 0.1, 0])
defect_index = 2

####### METHOD ######
def apply_ondulation(y, flawed_ply, defect_index):
    alpha = 0.55
    counter = defect_index
    while counter < np.size(y,0):
        a = y[counter]
        b = a - flawed_ply * np.exp(-alpha * (counter - defect_index))
        y[counter] = b
        counter += 1
    return y

####### OUTPUT ######
result = apply_ondulation(y, flawed_ply, defect_index)
print(result)