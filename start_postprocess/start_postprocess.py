from make_geometry.interfaces import Laminate
import pandas as pd
from start_postprocess import interfaces as i

################ METHOD #################
def start_postprocess(Laminate : Laminate, target_directory : str, laminate_choice : int, experiment_label : str):
    experiment = i.get_laminate_data(Laminate, experiment_label, laminate_choice)
    filename = target_directory + r"\input_analysis.spcf"
    applied_force = i.read_spcf(filepath= filename)
    i.calculate_stiffness(Laminate, experiment, applied_force)
    unified_results = i.update_results(experiment)
    


    

    

################ OUTPUT #################

