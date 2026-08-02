from test_generate_spline import generate_spline
import numpy as np
from test_get_max_ondulation import get_max_ondulation

################## INPUT #########################
x0 = 0.135
y0 = 0.375
y1 = 0.4946
dir = 1
c_gap = 0.95 * 0.5
k_fixed = 0
smooth = 0.3
return_frac = 0.85
eps_end_frac = 0.03
xgrid = np.linspace(0, 5, 500)
y_up_vec = get_max_ondulation(xgrid, 0.5) + 0.5
npt = 600

################# METHOD ##########################
def generate_with_fixed_k(x0, y0, y1, dir,
                          c_gap, k_fixed, smooth,
                          return_frac, eps_end_frac,
                          xgrid, y_up_vec, npt):
    s_lo = 0.55 + 0.35 * (1 -smooth)
    s_hi = 0.55 + 0.35 * (smooth)

    s_lo = min(max(s_lo, 0.45), 1.00)
    s_hi = min(max(s_hi, 0.45), 1.00)

    xb, yb = generate_spline(x0, y0, y1, dir, c_gap*k_fixed,
                             s_lo, s_hi, return_frac,
                             eps_end_frac, xgrid,
                             y_up_vec, npt)
    return xb, yb

############ OUTPUT ###################
if __name__ == "__main__":
    xb, yb = generate_with_fixed_k(x0, y0, y1, dir, c_gap,
                        k_fixed, smooth, return_frac,
                        eps_end_frac, xgrid, y_up_vec,
                        npt)