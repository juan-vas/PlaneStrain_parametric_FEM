import os
from datetime import datetime

def create_directory(workspace : str, label : str):
    folder_name = name_folder(label)
    target_directory = make_directory(folder_name, workspace)
    return target_directory

def name_folder(input = None):
    if input == None:
        today_object = datetime.now()
        folder_name = today_object.strftime("%y%m%d%H%M")
    else:
        folder_name = str(input)
    return folder_name

def make_directory(input : str, workspace :str):
    directory_name = workspace + input

    # Create the directory
    try:
        os.mkdir(directory_name)
        print(f"Directory '{directory_name}' created successfully.")
    except FileExistsError:
        print(f"Directory '{directory_name}' already exists.")
    except PermissionError:
        print(f"Permission denied: Unable to create '{directory_name}'.")
    except Exception as e:
        print(f"An error occurred: {e}")
    
    output = directory_name
    return output