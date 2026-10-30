import pandas as pd

############ INPUT ###################
property_index = pd.read_csv('sample_property_index.csv')

############ METHOD ##################
def prepare_pshell(property_index: pd.DataFrame):
    pshell_collection = []
    for row in property_index.itertuples():
        entry_1 = f"PSHELL,{row.pid},{row.mid},{row.shell_thickness}"
        entry_2 = f'$HMNAME PROP {row.pid} "{row.name}"'
        pshell_collection.append(entry_1)
        pshell_collection.append(entry_2)
    return pshell_collection

############ OUTPUT ##################
result = prepare_pshell(property_index)
print(result)
