import os
import numpy as np
import pandas as pd

############################## INPUT ##################################
spcf_file = r"C:\Users\juanv\Documents\Work\01 Politecnico de Madrid\99 TFM\04 Hypermesh Sessions\Laminate_01_Defect_0_at_04_w_0.00\input_analysis.spcf"


############################## METHOD ###################################
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
        result = np.sum(fx)
    return result

################################## OUTPUT ###########################################
# --- Example Workflow Execution ---
if __name__ == "__main__":
    try:
        # 1. Convert file contents into the filtered array
        fx_data = read_spcf(spcf_file)
        
        # 3. Print 
        print(fx_data)

            
    except Exception as error:
        print(f"Processing error: {error}")
