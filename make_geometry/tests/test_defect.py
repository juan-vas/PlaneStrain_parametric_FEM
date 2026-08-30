

########### INPUT ############
ply_with_defect_index = 4
defect_width = 0.5
# Defect Type
## Ondulation   : 0
## Gap          : 1
defect_type = 1

########### METHOD ############
class Defect:
    def __init__(self, ply_with_defect_index: int, defect_width: float, defect_type: int):
        self.ply_with_defect_index = ply_with_defect_index
        self.defect_width = defect_width
        self.defect_type = defect_type

    def display_defect_type(self):
        if self.defect_type == 0:
            print("The Laminate has an Ondulation Defect")
        if self.defect_type == 1:
            print("The Laminate has a Gap defect")

########### OUTPUT ############
defect = Defect(ply_with_defect_index, defect_width, defect_type)
defect.display_defect_type()
