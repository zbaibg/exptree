# exptree

A tool to manage experiment directories and their metadata using YAML files and CSV summaries.

## Overview

`exptree` helps you organize experimental runs by:
- Collecting metadata from `notes.yaml` files in subdirectories into a central `notes_summary.csv`
- Updating individual `notes.yaml` files based on the central CSV
- Creating new experiment directories from predefined templates

## Philosophy
Balancing human creativity with machine automation is a challenging task during **computational scientific exploration**—especially in its early, exploratory stages. During this phase, experimental runs often differ significantly in structure, the number and type of input parameters, and even in the underlying software architecture. Attempting to automate too early—for example, by writing scripts to parse outputs or enforce rigid formats—can be counterproductive, as the experimental landscape is still shifting.

This trial-and-error process is akin to reinforcement learning or generative thinking, where the human brain explores a range of possibilities without predefined structure. As such, conventional automation tools like grid search or batch analysis pipelines may fail to accommodate the irregularity of files and results.

`exptree` embraces this flexibility. It is not just a toolkit—it represents a workflow philosophy. Users manually maintain `notes.yaml` files within each run directory to record metadata, parameters, and observations. `exptree` provides tools to collect these YAML files into a centralized `notes_summary.csv` for easier inspection and analysis. It also allows users to push changes from the CSV back into the individual YAML files.

This workflow prioritizes human readability and adaptability over rigid automation. It allows users to explore freely and iteratively refine their experiments. Once the file structures and output formats stabilize, users may optionally write lightweight scripts to automatically update information—for example, by parsing output files and populating the CSV with results. However, `exptree` deliberately avoids enforcing this early on, preserving the creative freedom that is essential during the exploratory phase of computational science.

If you find this tool helpful, please consider giving it a star on GitHub :)

## Scripts Overview

- **collect_notes.py**: Aggregates metadata from all `notes.yaml` files into a central CSV
- **update_notes.py**: Synchronizes `notes.yaml` files with the central CSV
- **newrun.py**: Generates new experiment directories using template folders

## Directory Structure

Directories must follow one of these naming conventions:
1. `template*` – Template directories used to generate new runs
2. `run<number>` – Experiment run directories (automatically created by `newrun.py`)

Each directory should contain a `notes.yaml` file with metadata about the experiment.

A typical directory structure:

```
exptree/
├── template/
│   └── notes.yaml
├── template_advanced/
│   └── notes.yaml
├── run1/
│   └── notes.yaml
├── run2/
│   └── notes.yaml
├── run3/
│   └── notes.yaml
├── notes_summary.csv
├── newrun.py
├── collect_notes.py
└── update_notes.py
```

## YAML File Format

To preserve comments in `notes.yaml` files during updates:
- Place comments inline with keys (e.g., `key: value  # This comment will be preserved`)
- Comments on separate lines may be lost during updates

The YAML files must contain at least an `id` key, and its value must match the name of the directory it resides in.

## Special Values in CSV

The `notes_summary.csv` file recognizes two special string values:

- `yaml_empty`: Keeps the key in the YAML file but sets its value to null/empty
- `yaml_no_key`: Removes the key from the YAML file (used for padding YAML files with different numbers of keys)
- Blank cells in the CSV are treated as `yaml_no_key`

## Scripts

### collect_notes.py

Aggregates metadata from all `notes.yaml` files into a central `notes_summary.csv`.

**Usage:**
```bash
python collect_notes.py [--write]
```

**Options:**
- `--write`: Apply changes to `notes_summary.csv` (default is preview mode)

**Notes:**
- Adds new or changed YAML entries to the CSV
- Does not remove CSV rows for directories that no longer exist

### update_notes.py

Synchronizes individual `notes.yaml` files with `notes_summary.csv`.

**Usage:**
```bash
python update_notes.py [--write]
```

**Options:**
- `--write`: Apply changes to `notes.yaml` files (default is preview mode)

**Notes:**
- Adding or deleting CSV rows will not create or delete `notes.yaml` files and relevant folders.
- Keys in the YAML files **that need to be modified** are reordered to match CSV column order
- `yaml_empty` becomes an empty/null value
- `yaml_no_key` results in key deletion
- Blank cells in the CSV are treated as `yaml_no_key`
- Inline comments are preserved

### newrun.py

Creates a new experiment run by copying a template directory.

**Usage:**
```bash
python newrun.py <template_dir>
```

**Arguments:**
- `template_dir`: Path to the template directory to copy

**Behavior:**
1. Determines the next available `run<number>` name
2. Copies the contents of the template directory
3. Updates the `id` field in `notes.yaml` to match the new directory name
