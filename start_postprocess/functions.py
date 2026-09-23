import os
import numpy as np
import pandas as pd
from make_geometry.interfaces import Laminate, Defect

def get_laminate_data(Laminate: Laminate, experiment_label : str, laminate_choice):
    defect = Laminate.defect
    experiment = {
        "experiment_label" : experiment_label,
        "laminate_id" : laminate_choice,
        "defect_type" : defect.defect_type,
        "ply_with_defect_index" : defect.ply_with_defect_index,
        "defect_width" : defect.defect_width,
        "ply_thickness" : Laminate.ply_thickness,
        "ply_width" : Laminate.ply_width,
    }
    return experiment

def read_spcf(file_path):
    fx = []
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The specified file could not be found: {file_path}")
        
    with open(file_path, 'r') as file:
        for line in file:
            cleaned_line = line.strip()
            if not (cleaned_line and cleaned_line[0].isdigit()):
                continue
            tokens = cleaned_line.split()
            tokens = float(tokens[1])
            fx.append(tokens)
        fx = np.array(fx)
        applied_force = np.sum(fx)
    return applied_force

def calculate_stiffness(experiment : dict, force, area, strain, displacement):
    equivalent_stress = force / area
    equivalent_stiffness = equivalent_stress / strain
    laminate_rigidity = force / displacement
    # beam_rigidity = equivalent_stiffness * area / 5
    experiment["applied_force"] = force
    experiment["equivalent_stiffness"] = equivalent_stiffness
    experiment["laminate_rigidity"] = laminate_rigidity

def update_results(experiment : dict):
    try:
        unified_results = pd.read_csv('unified_results.csv')
    except:
        print('Creating unified_results database')
        unified_results = pd.DataFrame([experiment])
        unified_results.to_csv('unified_results.csv', index=False)
        return unified_results
    new_row = pd.DataFrame([experiment])
    unified_results = pd.concat([unified_results, new_row], 
              ignore_index= True)
    return unified_results

