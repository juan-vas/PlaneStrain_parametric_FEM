import shutil

def delete_directory(target_directory):
# Deletes the folder and everything inside it
    try:
        shutil.rmtree(target_directory)
        print("Directory and all its contents deleted successfully.")
    except FileNotFoundError:
        print("The directory does not exist.")
    except PermissionError:
        print("Permission denied: You cannot delete this folder.")
