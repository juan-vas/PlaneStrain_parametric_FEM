import pandas as pd

################ INPUT ##########################
element_index = pd.read_csv('sample_element_index.csv')

################ METHOD #########################
def prepare_cquad4(element_index : pd.DataFrame):
    cquad_collection = []
    for row in element_index.itertuples():
        entry = f"CQUAD4,{row.element_id},{row.pid},{row.node_a},{row.node_b},{row.node_c},{row.node_d}"
        cquad_collection.append(entry)
    return cquad_collection

################ OUTPUT #########################
result = prepare_cquad4(element_index)
print(result)
