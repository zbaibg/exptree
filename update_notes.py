#!/usr/bin/env python3
import os
import argparse
from utils import get_df_from_folders, get_df_from_csv, compare_two_df, STRING_YAML_EMPTY, STRING_YAML_NO_KEY, write_yaml_from_csv



def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Update yaml files from notes_summary.csv')
    parser.add_argument('--write', action='store_true', help=f'Write changes to files (default: preview only). Ignore the extra ids in extra ids either in notes_summary.csv or in the folders. Namely no creation or deletion of yaml files will be performed. For the yaml files to modify, its key sequence will be sorted to follow the order of columns in notes_summary.csv. {STRING_YAML_EMPTY} in csv will be converted to None in yaml, while keys with value {STRING_YAML_NO_KEY} in csv will be deleted in yaml. All blank values in csv is assumed as {STRING_YAML_NO_KEY} when loading the csv.')
    args = parser.parse_args()

    has_changes_in_all = False
    
    # Get data from CSV
    if not os.path.exists('notes_summary.csv'):
        print("Error: notes_summary.csv not found")
        return
    
    csv_df = get_df_from_csv()
    print("Loaded notes_summary.csv")
    
    # Get current data from yaml files
    folder_df = get_df_from_folders()
    
    # Compare the dataframes
    ids_only_in_csv, ids_only_in_folders, changed_value_in_csv_id_column, changed_value_in_folders_id_column = compare_two_df(csv_df,folder_df)
    
    if len(ids_only_in_csv) > 0:
        print(f"\nThe following ids are in the CSV but their folders are not found. These will be ignored:")
        for i, id in enumerate(ids_only_in_csv):
            print(f"{i+1}: {id}")
    
    if len(ids_only_in_folders) > 0:
        print(f"\nThe following ids are in folders but not in the CSV. These will be ignored:")
        for i, id in enumerate(ids_only_in_folders):
            print(f"{i+1}: {id}")
    
    if len(changed_value_in_csv_id_column) > 0:
        has_changes_in_all = True
        print("\nChanges in notes.yaml in each folder:")
        for id in changed_value_in_csv_id_column.keys():
            changed_value_in_csv_column = changed_value_in_csv_id_column[id]
            changed_value_in_folder_column = changed_value_in_folders_id_column[id]
            print(f"\nChanges in ./{id}/notes.yaml:")
            for col in changed_value_in_csv_column.keys():
                print(f"  {col}: {changed_value_in_folder_column[col]} -> {changed_value_in_csv_column[col]}")
                
    # Handle changes based on --write flag
    if has_changes_in_all:
        if args.write:
            write_yaml_from_csv(changed_value_in_csv_id_column,csv_df.columns)
        else:
            print("\n" + "="*80)
            print("This is a preview mode. No changes have been written to the yaml files.")
            print("To apply these changes, run the command with --write flag:")
            print(f"python {os.path.basename(__file__)} --write")
            print("="*80)
    else:
        print("\nNo changes detected.")


if __name__ == "__main__":
    main() 