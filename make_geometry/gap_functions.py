import numpy as np
from scipy.interpolate import PchipInterpolator
from functions import get_max_ondulation
import matplotlib.pyplot as plt


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
    m_end = get_local_slope(xgrid, y_up_vec, x_end)
    v_end = np.array([-dir, -dir * m_end])
    v_end = v_end / max(np.linalg.norm(v_end), eps_end_frac)
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

def generate_spline_with_fixed_k(x0, y0, y1, dir,
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

    xb_lo, yb_lo = generate_spline(
        x0, y0, y1, dir, c_gap_klo, s_lo, s_hi,
        return_frac, eps_end_frac, xgrid, y_up_vec, npt 
    )

    ok_lo = check_clearance(xb_lo, yb_lo,
                                                 xgrid, y_low_vec,
                                                 y_up_vec, gap_LR, tol)
    xb_hi, yb_hi = generate_spline(
        x0, y0, y1, dir, c_gap_khi, s_lo, s_hi,
        return_frac, eps_end_frac, xgrid,
        y_up_vec, npt
    )
    ok_hi = check_clearance(
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
        xb_m, yb_m = generate_spline(
            x0, y0, y1, dir, c_gap_km,
            s_lo, s_hi, return_frac, eps_end_frac,
            xgrid, y_up_vec, npt
        )
        ok_m = check_clearance(
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

    xb_best = xb_lo
    yb_best = yb_lo
    k_best = klo

    return k_best

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

def get_gap_intersection(x, x_points, y_points):
    y_intersection = np.interp(x, x_points, y_points)
    return y_intersection