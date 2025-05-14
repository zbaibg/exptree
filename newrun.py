#!/usr/bin/env python3
import os
import shutil
import re
import argparse
from ruamel.yaml import YAML

def get_max_run_index():
    """Find the maximum run index in the current directory"""
    max_index = -1
    for item in os.listdir('.'):
        if os.path.isdir(item):
            match = re.match(r'run(\d+)', item)
            if match:
                index = int(match.group(1))
                max_index = max(max_index, index)
    return max_index

def create_new_run(template_dir):
    """Create a new run directory by copying the template directory"""
    if not os.path.exists(template_dir):
        print(f"Error: Template directory '{template_dir}' does not exist!")
        return
    
    max_index = get_max_run_index()
    new_index = max_index + 1
    new_run_dir = f'run{new_index}'
    
    try:
        # Copy with symlinks=True to preserve symbolic links
        shutil.copytree(template_dir, new_run_dir, symlinks=True)
        # Update notes.yaml
        notes_path = os.path.join(new_run_dir, 'notes.yaml')
        if os.path.exists(notes_path):
            yaml = YAML()
            yaml.preserve_quotes = True
            with open(notes_path, 'r') as f:
                notes = yaml.load(f)
            notes['id'] = new_run_dir
            with open(notes_path, 'w') as f:
                yaml.dump(notes, f)
        print(f"Successfully created new run directory: {new_run_dir}")
    except Exception as e:
        print(f"Error creating new run directory: {str(e)}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create a new run directory by copying a template directory')
    parser.add_argument('template_dir', help='Path to the template directory to copy')
    args = parser.parse_args()
    
    create_new_run(args.template_dir) 