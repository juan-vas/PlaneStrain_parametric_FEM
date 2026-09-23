import pandas as pd

########### INPUT ##########
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

########### METHOD ##########
def update_results(experiment : dict):
    try:
        unified_results = pd.read_csv('unified_results.csv')
    except:
        print('Creating unified_results database')
        unified_results = pd.DataFrame([experiment])
        unified_results.to_csv('unified_results.csv', index= False)
        return unified_results
    new_row = pd.DataFrame([experiment])
    unified_results = pd.concat([unified_results, new_row], 
              ignore_index= True)
    return unified_results

############ OUTPUT ##########
result = update_results(experiment)
print(result)