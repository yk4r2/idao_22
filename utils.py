import csv
import json
import yaml
from tqdm import tqdm
from pathlib import Path
from pymatgen.core import Structure
from typing import Dict as D, List as L, Tuple as T, Union as U


def read_config(path: Path) -> D[str, str]:
    """ reads config with data paths and specific options """
    with open(path, 'r') as f:
        return yaml.full_load(f)


def write_csv(data: L[D[str, str]], path: Path, fieldnames: L[str]) -> None:
    """ writes list of dicts to csv file, where each dict in list has same keys"""
    with open(path, 'w') as f:
        writer = csv.DictWriter(f, fieldnames)
        writer.writeheader()
        writer.writerows(data)


def read_structures(
    root: Path, with_targets=False
) -> U[D[str, Structure], T[D[str, Structure], L[D[str, str]]]]:
    """
    takes path to the root of data and reads structures from .json file
    to dict, where keys are ids and values are pymatgen.core.Structure objects

    Args:
        root (Path): path to data (for example data/dichalcogenides_private)
        with_targets (bool, optional): whether to read targets from target.csv file.
            Defaults to False.

    Returns:
        U[D[str, Structure], T[D[str, Structure], L[D[str, str]]]]: 
    dictionary of structures or tuple with dictionary of structures and targets band gap
    
    """
    root = Path(root) if isinstance(root, str) else root
    folder_contains = tuple(i.name for i in root.iterdir())
    assert root.exists(), f'No folder exists at {root}'
    assert root.is_dir(), f'root variable must point at folder'
    assert 'structures' in folder_contains, f'structure/ folder is not found in {folder_contains}'

    structures = {}
    for structure_path in tqdm((root / 'structures').glob('*.json')):
        with open(structure_path, 'r') as f:
            struct = Structure.from_dict(json.load(f))
            structures.update({structure_path.name.strip('.json'): struct})

    if with_targets:
        assert 'targets.csv' in (i.name for i in root.iterdir()), f'targets.csv is not found in {root}'
        targets = read_csv(root / 'targets.csv')
        return structures, targets

    return structures


def read_csv(root: Path, delimiter=',', quotechar='|', newline='') -> L[D[str, str]]:
    """ reads csv to list of dicts """
    with open(root, newline=newline) as f:
        return [i for i in csv.DictReader(f, delimiter=delimiter, quotechar=quotechar)]
