import shutil
import numpy as np
import glob
import os
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap
import ast
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
def write_yaml_from_csv(changed_value_in_csv_id_column,column_order):
    '''The order of the columns will be written to the yaml as in column_order'''
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.indent(mapping=2, sequence=2, offset=0)
    
    for id in changed_value_in_csv_id_column.keys():
        changed_value_in_csv_column = changed_value_in_csv_id_column[id]
        yaml_file = f'{id}/notes.yaml'
        backup_file = f'{id}/notes.yaml.bk'
        
        # Create backup
        shutil.copy2(yaml_file, backup_file)
        
        # Load existing YAML with preserved order
        with open(yaml_file, 'r') as f:
            yaml_data = yaml.load(f)
        
        # Update values
        for col, value in changed_value_in_csv_column.items():
            if value==STRING_YAML_NO_KEY:
                if col in yaml_data:
                    yaml_data.pop(col)
            elif value==STRING_YAML_EMPTY:
                yaml_data[col] = None
            else:
                try:
                    yaml_data[col] = ast.literal_eval(value) # Convert non-string values to its possible types
                except:
                    yaml_data[col] = value # If cannot convert to other types, keep it as string
                
        # Sort the yaml data according to the column order while keeping the comments
        yaml_data = sort_yaml_keys_keep_comments(yaml_data,column_order)
        # Write back to file
        with open(yaml_file, 'w') as f:
            yaml.dump(yaml_data, f)
def sort_yaml_keys_keep_comments(yaml_data: CommentedMap, column_order: list) -> CommentedMap:
    # Create a new map to store the sorted data
    new_map = CommentedMap()
    
    # First add keys that are in column_order in that order
    for key in column_order:
        if key in yaml_data:
            new_map[key] = yaml_data[key]
            # Preserve comments if they exist
            if key in yaml_data.ca.items:
                new_map.ca.items[key] = yaml_data.ca.items[key]
    
    # Then add any remaining keys that weren't in column_order
    for key in yaml_data:
        if key not in column_order:
            new_map[key] = yaml_data[key]
            # Preserve comments if they exist
            if key in yaml_data.ca.items:
                new_map.ca.items[key] = yaml_data.ca.items[key]
    
    return new_map
def modify_yamls_by_func(func,check_template=False,write=False):
    """
    The func should take a df and return a df. It should not create or delete any rows. It should not change the index or id column of the df.
    If write is True, the function will write the changes to the yaml files. Otherwise, it will only print the changes.
    """
    df_old = get_df_from_folders()
    if not check_template:
        template_index=[]
        for index,row in df_old.iterrows():
            if row['id'].startswith('template'):
                template_index.append(index)
        df_old=df_old.drop(template_index,axis=0)
    index_in_df_old=df_old.index
    df_modified = func(df_old)
    id_in_df_modified=df_modified['id']
    assert set(df_modified.index) == set(index_in_df_old), "The index of the modified df should be the same as the old df"
    assert set(id_in_df_modified) == set(index_in_df_old), "The id column of the modified df should be the same as the old df"
    id_only_in_df_old, id_only_in_df_modified, changed_value_in_df_old_id_column,changed_value_in_df_modified_id_column=compare_two_df(df_old,df_modified)

    if len(changed_value_in_df_old_id_column) > 0:
        has_changes_in_all = True
        print("\nChanges in notes.yaml in each folder:")
        for id in changed_value_in_df_old_id_column.keys():
            changed_value_in_df_old_column = changed_value_in_df_old_id_column[id]
            changed_value_in_df_modified_column = changed_value_in_df_modified_id_column[id]
            print(f"\nChanges in ./{id}/notes.yaml:")
            for col in changed_value_in_df_old_column.keys():
                print(f"  {col}: {changed_value_in_df_old_column[col]} -> {changed_value_in_df_modified_column[col]}")
    if write:
        write_yaml_from_csv(changed_value_in_df_modified_id_column,df_modified.columns)
        print("Yaml files have been updated.")
    else:
        print("\n" + "="*80)
        print("This is a preview mode. No changes have been written to the yaml files.")
        print("To apply these changes, run the command with --write flag:")
        print("="*80)
