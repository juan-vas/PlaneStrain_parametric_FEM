import numpy as np
############ INPUT ##############
x = np.linspace(0,5,6)
y = np.array([[0, 1, 2, 3]])
y = np.repeat(y, 6, axis=0)
y = np.transpose(y)

############# METHOD ################
def create_auxiliary_curves(x, y):
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


########### OUTPUT ##################
result = create_auxiliary_curves(x, y)
print(result)