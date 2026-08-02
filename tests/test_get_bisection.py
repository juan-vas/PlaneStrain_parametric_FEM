import numpy as np
from test_get_max_ondulation import get_max_ondulation
import matplotlib.pyplot as plt
import test_check_clearance
import test_generate_spline
############ INPUT ###########
x0 = 0.135
y0 = 0.3750
y1 = 0.4946
dir = 1
c_gap = 0.95 * 0.5
smooth = 0.3
xgrid = np.linspace(0.0, 5.0, 500)
y_low_vec = np.ones(500) * 0.3750
y_up_vec = get_max_ondulation(xgrid, 0.5) + 0.5
gap_LR = np.array([0.135, 2.7500])
tol = 0.002
npt = 600
kmin = 0.35
max_iter = 28
return_frac = 0.85
eps_end_frac = 0.03

############ METHOD ###########
def get_bisection(x0, y0, y1, dir, c_gap, smooth, xgrid, y_low_vec, y_up_vec, gap_LR, tol, npt = None, kmin = None, 
                  max_iter = None,
                  return_frac = None, eps_end_frac = None):
    
    if eps_end_frac  == None: eps_end_frac = 0.03
    if return_frac == None: return_frac = 0.85
    if max_iter == None: max_iter = 28
    if kmin == None: kmin = 0.35
    if npt == None: npt = 600

    tol = max(tol, 0)

    s_lo = 0.55 + 0.35 * (1 - smooth)
    s_hi = 0.55 + 0.35 * smooth
    s_lo = min(max(s_lo, 0.45), 1.00)
    s_hi = min(max(s_hi, 0.45), 1.00)

    klo = kmin
    khi = 1.00
    c_gap_klo = c_gap * klo
    c_gap_khi = c_gap * khi

    xb_lo, yb_lo = test_generate_spline.generate_spline(
        x0, y0, y1, dir, c_gap_klo, s_lo, s_hi,
        return_frac, eps_end_frac, xgrid, y_up_vec, npt 
    )

    ok_lo = test_check_clearance.check_clearance(xb_lo, yb_lo,
                                                 xgrid, y_low_vec,
                                                 y_up_vec, gap_LR, tol)
    xb_hi, yb_hi = test_generate_spline.generate_spline(
        x0, y0, y1, dir, c_gap_khi, s_lo, s_hi,
        return_frac, eps_end_frac, xgrid,
        y_up_vec, npt
    )
    ok_hi = test_check_clearance.check_clearance(
        xb_hi, yb_lo, xgrid, y_low_vec, y_up_vec,
        gap_LR, tol
    )

    if (not ok_lo) and (not ok_hi):
        xb_best = xb_lo
        yb_best = yb_lo
        k_best = klo 
        return k_best

    if ok_hi:
        xb_best = xb_hi
        yb_best = yb_hi
        k_best = khi
        return k_best

    for it in range(1, max_iter + 1):
        km = 0.5 * (klo + khi)
        c_gap_km = c_gap * km
        xb_m, yb_m = test_generate_spline.generate_spline(
            x0, y0, y1, dir, c_gap_km,
            s_lo, s_hi, return_frac, eps_end_frac,
            xgrid, y_up_vec, npt
        )
        ok_m = test_check_clearance.check_clearance(
            xb_m, yb_m, xgrid, y_low_vec, y_up_vec, gap_LR, tol
        )

        if ok_m:
            klo = km
            xb_lo = xb_m
            yb_lo = yb_m
        else:
            khi = km

        if abs(khi - klo) < 1e-3:
            break

    # xb_best = xb_lo
    # yb_best = yb_lo
    k_best = klo

    return k_best

############ OUTPUT ###########
if __name__ == "__main__":
    k_best = get_bisection(x0, y0, y1, dir, c_gap, smooth, xgrid, y_low_vec, y_up_vec, gap_LR, tol, npt, kmin, max_iter, return_frac, eps_end_frac)
    result = k_best
    print("this is the best" + str(k_best))

# fig, ax = plt.subplots()
# ax.plot(xb_best, yb_best, linewidth = 2.0)
# plt.show()
