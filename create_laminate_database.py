import pandas as pd
import choose_laminate as cl
import numpy as np
import ast

laminate_database = pd.read_csv('laminate_database.csv', index_col='laminate_id')
unified_results = pd.read_csv('unified_results.csv')
unified_results = unified_results[unified_results['defect_width'] == 1.00]
df = unified_results[['laminate_id', 'ply_with_defect_index']]
df = pd.merge(
    left= df,
    right= laminate_database,
    how= 'inner',
    on= 'laminate_id'
)
df['ply_sequence'] = df['ply_sequence'].apply(ast.literal_eval)
df['orientation_at_defect'] = df.apply(lambda row: row['ply_sequence'][row['ply_with_defect_index'] - 1], axis=1)
print(df.head())
