import numpy as np
import glob
import os
from ruamel.yaml import YAML
import pandas as pd
STRING_YAML_EMPTY='yaml_empty'
STRING_YAML_NO_KEY='yaml_no_key'
def read_notes_yaml(file_path):
    yaml = YAML()
    with open(file_path, 'r') as f:
        data = yaml.load(f)
        for key in data.keys():
            if data[key] is None:
                data[key] = STRING_YAML_EMPTY
    return data

def normalize_value(value):
    """Convert value to string for comparison"""
    if value is None or np.nan:
        return "null"
    if isinstance(value, (list, tuple)):
        return str([normalize_value(x) for x in value])
    return str(value).strip()

def get_df_from_folders():
    '''
    Get the df from the notes.yaml files in the run and template directories,
    the index of the df will be set to be the id column
    id is checked to be the same as the directory name
    '''
    # Find all run directories and template directories
    run_dirs = sorted(glob.glob('run[0-9]*'))
    template_dirs = sorted(glob.glob('template*'))
    # List to store all data
    all_data = []
    # Process each run directory
    for run_dir in run_dirs+template_dirs:
        yaml_file = os.path.join(run_dir, 'notes.yaml')
        if os.path.exists(yaml_file):
            data = read_notes_yaml(yaml_file)
            assert data['id'] == os.path.basename(run_dir)
            all_data.append(data)
    
    # Create DataFrame
    new_df = pd.DataFrame(all_data).fillna(value=STRING_YAML_NO_KEY)
    # Set 'id' as the index but keep it as a column as well
    new_df = new_df.set_index('id', drop=False)
    # Convert all columns to string type and strip whitespace
    for column in new_df.columns:
        new_df[column] = new_df[column].astype('string').str.strip()
    return new_df

def get_df_from_csv():
    '''
    Get the df from the notes_summary.csv file,
    the index of the df will be set to be the id column
    '''
    if os.path.exists('notes_summary.csv'):
        existing_df = pd.read_csv('notes_summary.csv').fillna(value=STRING_YAML_NO_KEY)
        existing_df = existing_df.set_index('id', drop=False)
        # Convert all columns to string type and strip whitespace
        for column in existing_df.columns:
            existing_df[column] = existing_df[column].astype('string').str.strip()
        return existing_df
    else:
        return None

def create_empty_df():
    '''
    Create an empty df with only one column, id
    the index of the df will be set to be the id column
    '''
    empty_df = pd.DataFrame(columns=['id'])
    empty_df = empty_df.set_index('id', drop=False)
    return empty_df

def compare_two_df(df1, df2):
    '''
    Compare two df
    '''
    df1=df1.copy()
    df2=df2.copy()
    all_col = set(df2.columns) | set(df1.columns)
    df1 = df1.reindex(columns=all_col,fill_value=STRING_YAML_NO_KEY)
    df2 = df2.reindex(columns=all_col,fill_value=STRING_YAML_NO_KEY)

    
    # Find new entries
    ids_df1 = set(df1.index)
    ids_df2 = set(df2.index)
    
    id_only_in_df1 = ids_df1 - ids_df2
    id_only_in_df2 = ids_df2 - ids_df1
    
    changed_value_in_df1_id_column={}#id:column_name:value in df1
    changed_value_in_df2_id_column={}#id:column_name:value in df2
    common_ids=list(ids_df1.intersection(ids_df2))
    
    df1_common=df1.loc[common_ids]
    df2_common=df2.loc[common_ids]
    
    # Compare values for common IDs
    # Create a mask where values are not equal between the two dataframes
    comparison_mask = df1_common != df2_common
    
    # Iterate through each row (ID) where there are differences
    for id in common_ids:
        # Get columns where values differ for this ID
        diff_columns = comparison_mask.loc[id][comparison_mask.loc[id] == True].index.tolist()
        diff_values_df1 = df1_common.loc[id][diff_columns]
        diff_values_df2 = df2_common.loc[id][diff_columns]
        # If there are differences, add them to the changed_key dictionary
        if diff_columns:
            changed_value_in_df1_id_column[id] = {diff_columns[i]:diff_values_df1.iloc[i] for i in range(len(diff_columns))}
            changed_value_in_df2_id_column[id] = {diff_columns[i]:diff_values_df2.iloc[i] for i in range(len(diff_columns))}
    # Return the dictionary of changes (id: list of changed columns)

    return id_only_in_df1, id_only_in_df2, changed_value_in_df1_id_column,changed_value_in_df2_id_column