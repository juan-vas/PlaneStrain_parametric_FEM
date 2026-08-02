def get_gap_intersection(x, x_points, y_points):
    y_intersection = np.interp(x, x_points, y_points)
    return y_intersection