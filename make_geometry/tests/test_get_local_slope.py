import numpy as np
from scipy.interpolate import PchipInterpolator

############## INPUT ##################
# Datos de prueba (una parábola y = x^2, su derivada debería ser 2x)
xv_test = np.linspace(0, 10, 100)
yv_test = xv_test**2

# Puntos de consulta (el 2.5 está dentro, el 5.0 está fuera/extrapolado)
xq_test = [1.0, 9.9]



############## METHOD ##################
def get_local_slope(xv, yv, xq):
    # 1. Asegurar que los datos sean arrays de NumPy
    xv = np.asarray(xv, dtype=float)
    yv = np.asarray(yv, dtype=float)
    xq = np.asarray(xq, dtype=float)
    
    # 2. Calcular el gradiente (equivalente a gradient(yv, xv) de MATLAB)
    dy = np.gradient(yv, xv)
    
    # 3. Crear el interpolador PCHIP (incluye extrapolación por defecto)
    interp_func = PchipInterpolator(xv, dy)
    
    # 4. Evaluar en los puntos de consulta (xq)
    m = interp_func(xq)
    
    return m

############## OUTPUT ##################
if __name__ == "__main__":
    result = get_local_slope(xv_test, yv_test, xq_test)
    print(result)  
    # Resultado aproximado: [5.  9.8] (la derivada exacta sería 5 y 10)