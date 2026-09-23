import pandas as pd

def create_unified_results():
    columns = [
        'experiment_label',
        'laminate_id', 
        'defect_type', 
        'ply_with_defect_index', 
        'defect_width',
        'ply_thickness', 
        'ply_width', 
        'applied_force', 
        'equivalent_stiffness', 
        'laminate_rigidity']
    unified_results = pd.DataFrame(columns= columns)
    unified_results.to_csv('unified_results.csv')

create_unified_results()