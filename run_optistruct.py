import os
import subprocess
###################### INPUT ###########################
bdf_file_path = r'C:\Users\juanv\Documents\Work\01 Politecnico de Madrid\99 TFM\05 Virtual Experiments\Laminate_01_Defect_0_at_02_w_0.00\input_analysis.bdf'
output_dir = r'C:\Users\juanv\Documents\Work\01 Politecnico de Madrid\99 TFM\05 Virtual Experiments\Laminate_01_Defect_0_at_02_w_0.00\\'
optistruct_exec = r'C:\Program Files\Altair\2026.1\hwsolvers\scripts\optistruct.bat'

###################### METHOD ###########################
def run_optistruct_analysis(bdf_file_path, output_dir, optistruct_exec=None):
    """
    Runs an OptiStruct analysis on a given .bdf file and ensures all 
    generated output files (.out, .h3d, .res, etc.) are saved in output_dir.
    """
    # 1. Resolve absolute paths
    bdf_abs_path = os.path.abspath(bdf_file_path)
    output_dir_abs = os.path.abspath(output_dir)
    bdf_filename = os.path.basename(bdf_abs_path)
    
    # 2. Create the target output directory if it doesn't exist
    os.makedirs(output_dir_abs, exist_ok=True)
    
    # 3. Copy the .bdf file into the target directory
    # OptiStruct generates files in the directory where the solver deck lives.
    target_bdf_path = os.path.join(output_dir_abs, bdf_filename)
    # shutil.copy2(bdf_abs_path, target_bdf_path)
    
    # 4. Locate the OptiStruct Executable (Default to common 2026 Student installation path)
    if optistruct_exec is None:
        # Update this path if you installed Altair 2026 in a custom directory
        optistruct_exec = r"C:\Program Files\Altair\2026\altair\hwsolvers\optistruct\bin\win64\optistruct.exe"
        
    if not os.path.exists(optistruct_exec):
        raise FileNotFoundError(f"OptiStruct executable not found at: {optistruct_exec}")
        
    # 5. Build the command line argument list
    # The '-opts' flags or standard inputs can be added here
    cmd = [optistruct_exec, target_bdf_path]
    
    print(f"Starting OptiStruct analysis for: {bdf_filename}...")
    print(f"Output files will populate in: {output_dir_abs}")
    
    try:
        # Run OptiStruct. We set cwd (current working directory) to the output folder.
        result = subprocess.run(
            cmd, 
            cwd=output_dir_abs, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True,
            check=True
        )
        print("Analysis completed successfully.")
        return True
        
    except subprocess.CalledProcessError as e:
        print("Error during OptiStruct analysis execution:")
        print(e.stderr)
        # Check the generated .out file in the directory for detailed solver errors
        return False

# --- Example Usage ---
# input_deck = "C:/Simulation_Projects/my_model.bdf"
# results_folder = "C:/Simulation_Projects/Analysis_Runs/Iteration_1"
# run_optistruct_analysis(input_deck, results_folder)

######################## OUTPUT ###################################
if __name__ == "__main__":
    run_optistruct_analysis(bdf_file_path, output_dir, optistruct_exec)
