from start_postprocess import functions as f
from make_geometry.interfaces import Laminate
import pandas as pd

def get_laminate_data(Laminate: Laminate, experiment_label: str, laminate_choice : int):
    experiment = f.get_laminate_data(Laminate, experiment_label, laminate_choice)
    return experiment

def read_spcf(filepath : str):
    applied_force = f.read_spcf(filepath)
    return applied_force

def calculate_stiffness(Laminate : Laminate, experiment : dict, applied_force : float):
    laminate_height = Laminate.ply_thickness * Laminate.number_of_plies
    shell_thickness = Laminate.ply_thickness
    area = laminate_height * shell_thickness
    ply_width = Laminate.ply_width
    displacement = 1.2
    strain = displacement / ply_width
    f.calculate_stiffness(experiment, applied_force, area, strain, displacement)

def update_results(experiment : dict):
    unified_results = f.update_results(experiment)
    unified_results.to_csv('unified_results.csv', index=False)
    return unified_results
