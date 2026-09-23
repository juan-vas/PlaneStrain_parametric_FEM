from test_read_spcf import read_spcf
import pandas as pd

#################### INPUT ############################
spcf_file = r"C:\Users\juanv\Documents\Work\01 Politecnico de Madrid\99 TFM\04 Hypermesh Sessions\Laminate_01_Defect_0_at_04_w_0.00\input_analysis.spcf"
experiment = {
    "experiment_label" : 'L01_D0_at_02_w_1.00',
    "laminate_id" : 1,
    "defect_type" : 0,
    "ply_with_defect_index" : 2,
    "defect_width" : 1.00,
    "ply_thickness" : 0.125,
    "ply_width" : 5.00,
}
force = read_spcf(spcf_file)
area = 8 * 0.125 * 0.125 # This seems wrong
strain = 0.12 / 5
displacement = 0.12

################### METHOD ##########################
def calculate_stiffness(experiment : dict, force, area, strain, displacement):
    equivalent_stress = force / area
    equivalent_stiffness = equivalent_stress / strain
    laminate_rigidity = force / displacement
    # beam_rigidity = equivalent_stiffness * area / 5
    experiment["applied_force"] = force
    experiment["equivalent_stiffness"] = equivalent_stiffness
    experiment["laminate_rigidity"] = laminate_rigidity

################# OUTPUT ##########################
calculate_stiffness(experiment, force, area, strain, displacement)
result = pd.DataFrame([experiment])
print(result)
