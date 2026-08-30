import sys

################ INPUT #################
number_of_plies = 8
ply_with_defect_index = 4
defect_width = 0.5
# Defect Type
## Ondulation   : 0
## Gap          : 1
defect_type = 1

############### METHOD #################

def check_input_validity(number_of_plies, ply_index, defect_width, defect_type : int):
    if not isinstance(number_of_plies, int):
        print("Unvalid Input: Number of plies needs to be an integer")
        sys.exit()
    
    if not number_of_plies > 1:
        print("Unvalid Input: Number of plies needs to be greater than one")
        sys.exit()

    if not isinstance(ply_index, int):
        print("Unvalid Input: Ply index needs to be an integer")
        sys.exit()

    if not ((ply_index > 1) and (ply_index < number_of_plies)):
        print("Unvalid Input: The index of the ply with the defect must be " \
        "greater than 1 and less than the total number of plies")
        sys.exit()

    if not (defect_width < 5.0 and defect_width > 0.0):
        print("Unvalid Input: Defect width needs to be 0 < x < 5 mm")
        sys.exit()

    if not ((defect_type == 0) or (defect_type == 1)):
        print("Unvalid Input: Unvalid defect type code")
        sys.exit()
    
    print("Inputs are valid")

    


############## OUTPUT ##################

check_input_validity(number_of_plies, ply_with_defect_index, defect_width, defect_type)