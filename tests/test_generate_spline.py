import numpy as np
from scipy.interpolate import PchipInterpolator
import test_get_local_slope
from test_get_max_ondulation import get_max_ondulation
import matplotlib.pyplot as plt


########## INPUT ##########
x0 = 0.135
y0 = 0.375
y1 = 0.4946
dir = 1
c_gap = 0.95 * 0.5
s_lo = 0.7950
s_hi = 0.6550
return_frac = 0.85
eps_end_frac = 0.03
xgrid = np.linspace(0, 5, 500)
y_up_vec = get_max_ondulation(xgrid, 0.5) + 0.5
npt = 600
########## METHOD ##########
def generate_spline(x0, y0, y1, dir, c_gap, s_lo, s_hi, return_frac, eps_end_frac, xgrid, y_up_vec, npt = None):
    if npt == None: npt = 70

    # Avance/retorno (forma base)
    c1 = c_gap * (0.65 * s_lo)
    c2 = c_gap * (1.00 * s_lo)
    c3 = c_gap * (0.95 * s_hi)
    c4 = c_gap * (0.75 * s_hi)

    back = return_frac * c4
    tail_len = max(eps_end_frac * c_gap, 0.10 * back)

    # Puntos de control iniciales (barriga)
    P0 = np.array([x0, y0])
    P1 = np.array([x0 + dir * c1, y0])  # y'(0) = 0
    P2= np.array([x0 + dir * c2, y0])              # y''(0) = 0
    P3 = np.array([x0 + dir * c3, y1])             # Mantenemos para no tocar la barriga

    # Cierre exacto y tangente sobre la superior, 
    # garantizando x monótono en retorno
    x_end = x0 - dir * (back + tail_len)
    y_end_interpolation_function = PchipInterpolator(xgrid, y_up_vec)
    y_end = y_end_interpolation_function(x_end)
    m_end = test_get_local_slope.get_local_slope(xgrid, y_up_vec, x_end)
    v_end = np.array([-dir, -dir * m_end])
    v_end = v_end / max(np.linalg.norm(v_end), eps_end_frac) # are u sure?
    L_end = 0.75 * c4

    P5 = np.array([x_end, y_end])
    P4 = P5 - (L_end * v_end)

    # Seguridad:Unimodalidad estricta del retorno
    if dir == +1:
        P4[0] = max(min(P4[0], P3[0]-1e-9), P5[0]+1e-9)
    else:
        P4[0] = min(max(P4[0], P3[0]+1e-9), P5[0]-1e-9)

    # Evalúa Bézier quíntica
    t = np.linspace(0, 1, npt)
    u = 1 - t
    B0 = u ** 5
    B1 = 5 * u ** 4 * t
    B2 = 10 * u ** 3 * t ** 2
    B3 = 10 * u **2 * t ** 3
    B4 = 5 * u * t ** 4
    B5 = t ** 5

    xb = (B0 * P0[0] +
          B1 * P1[0] +
          B2 * P2[0] +
          B3 * P3[0] +
          B4 * P4[0] +
          B5 * P5[0])
        
    yb = (B0 * P0[1] +
          B1 * P1[1] +
          B2 * P2[1] +
          B3 * P3[1] +
          B4 * P4[1] +
          B5 * P5[1])

    return xb, yb


        
########## OUTPUT ##########
if __name__ == "__main__":
    xb, yb = generate_spline(x0, y0, y1, dir, c_gap,
                            s_lo, s_hi, return_frac,
                            eps_end_frac, xgrid,
                            y_up_vec, npt)
    print(xb)

