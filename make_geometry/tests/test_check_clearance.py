import numpy as np
import test_generate_spline as tgs
from test_get_max_ondulation import get_max_ondulation

######### INPUT #########
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

xb, yb = tgs.generate_spline(x0, y0, y1, dir, c_gap, s_lo, s_hi, return_frac, eps_end_frac, xgrid, y_up_vec, npt)


y_low_vec = np.ones(500) * 0.3750
gap_LR = np.array([0.135, 2.7500])
tol = 0.002

######### METHOD #########
def check_clearance(xb, yb, xgrid, y_low_vec, y_up_vec, gap_LR, tol):
    xb = np.minimum(np.maximum(xb, gap_LR[0]), gap_LR[1])
    y_low_i = np.interp(xb, xgrid, y_low_vec)
    y_up_i = np.interp(xb, xgrid, y_up_vec)
    clr_low = yb - y_low_i
    clr_up = y_up_i - yb
    min_low = np.min(clr_low)
    min_up = np.min(clr_up)
    ok = (min_low >= tol) and (min_up >= tol)
    return ok

######### OUTPUT #########
if __name__ == "__main__":
    result = check_clearance(xb, yb, xgrid, y_low_vec, y_up_vec, gap_LR, tol)
    print(result)