#!/usr/bin/env python3
import os
import pandas as pd
import argparse
from utils import get_df_from_folders, get_df_from_csv, create_empty_df, compare_two_df, STRING_YAML_NO_KEY, write_csv_from_df, to_ignore_float_error



def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Collect and compare notes from yaml files')
    parser.add_argument('--write', action='store_true', help='Write changes to files (default: preview only). Ignore the extra ids in the new notes_summary.csv. Namely the program will not delete any row in the notes_summary.csv.')
    parser.add_argument('--ignore_float_error', action='store_true', help='Ignore float error when comparing information in the notes.yaml files with the notes_summary.csv')
    parser.add_argument('--abs_error', type=float, default=1e-15, help='Absolute error for float comparison.')
    parser.add_argument('--rel_error', type=float, default=1e-15, help='Relative error for float comparison.')
    args = parser.parse_args()

    has_changes_in_all = False
    
    # Get new data from yaml files
    folder_df = get_df_from_folders()

    # Load existing data if available
    if os.path.exists('notes_summary.csv'):
        csv_df = get_df_from_csv()
        print("Found existing notes_summary.csv")
    else:
        #save an empty dataframe
        csv_df = create_empty_df()
        print("No existing notes_summary.csv found, will create an empty one")
    
    # Find new entries
    ids_only_in_csv, ids_only_in_folders, changed_value_in_csv_id_column,changed_value_in_folders_id_column=compare_two_df(csv_df,folder_df)
    if args.ignore_float_error:
        changed_value_in_csv_id_column,changed_value_in_folders_id_column=to_ignore_float_error(changed_value_in_df1_id_column=changed_value_in_csv_id_column,changed_value_in_df2_id_column=changed_value_in_folders_id_column,abs_error=args.abs_error,rel_error=args.rel_error)

    if len(ids_only_in_csv) > 0:
        print(f"The following ids are in the existing notes_summary.csv but their folders are not found. These will be kept as is:")
        extra_df=csv_df[list(ids_only_in_csv)]
        new_df=pd.concat([folder_df,extra_df])
    else:
        new_df=folder_df    
    if len(ids_only_in_folders) > 0:
        has_changes_in_all = True
        print("\nNew entries found, the following ids will be added to the notes_summary.csv:")
        for i, id in enumerate(ids_only_in_folders):
            print(f"{i+1}: {id}")
    
    if len(changed_value_in_csv_id_column) > 0:
        has_changes_in_all = True
        print("\nChanges in the existing notes_summary.csv:")
        for id in changed_value_in_csv_id_column.keys():
            changed_value_in_csv_column = changed_value_in_csv_id_column[id]
            changed_value_in_folder_column = changed_value_in_folders_id_column[id]
            print(f"\nChanges in {id}:")
            for col in changed_value_in_csv_column.keys():
                print(f"  {col}: {changed_value_in_csv_column[col]} -> {changed_value_in_folder_column[col]}")
                
    # Handle changes based on --write flag
    if has_changes_in_all:
        if args.write:
            write_csv_from_df(new_df)
        else:
            print("\n" + "="*80)
            print("This is a preview mode. No changes have been written to the notes_summary.csv.")
            print("To apply these changes, run the command with --write flag:")
            print(f"python {os.path.basename(__file__)} --write")
            print("="*80)
    else:
        print("\nNo changes detected.")

if __name__ == "__main__":
    main() 