import pandas as pd

unified_results = pd.read_csv('unified_results.csv')

experiment = {
    "experiment_label" : 'L01_D0_at_02_w_1.00',
    "laminate_id" : 1,
    "defect_type" : 0,
    "ply_with_defect_index" : 2,
    "defect_width" : 1.00,
    "ply_thickness" : 0.125,
    "ply_width" : 5.00,
    "applied_force" : 1000.0,
    "equivalent_stiffness" : 1000.0,
    "laminate_rigidity" : 1000.0
}

new_row = pd.DataFrame([experiment])
print(unified_results)
print(new_row)
unified_results = pd.concat([unified_results, new_row], ignore_index= True)
print(unified_results)