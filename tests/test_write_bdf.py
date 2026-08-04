############# INPUT #############
filename = "example.txt"
x = ["sdf\n", "vdfv\n"]

############ METHOD ############
def write_bdf(filename, collection):
    with open(filename, "w", encoding="utf-8") as file:
        file.writelines(collection)


############# OUTPUT #############
write_bdf(filename,x)