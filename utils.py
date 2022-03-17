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


def read_structures(json_path: Path) -> D[str, Structure]:
    """
    takes path to the root of data and reads structures from .json file
    to dict, where keys are ids and values are pymatgen.core.Structure objects

    Args:
        root (Path): path to json data (for example data/train/defects/pymatgen)

    Returns:
        D[str, Structure]: dictionary of structures 

    """
    json_path = Path(json_path) if isinstance(json_path, str) else json_path
    assert json_path.exists(), f'No folder exists at {json_path}'
    assert json_path.is_dir(), f'root variable must point at folder'

    structures = {}
    for structure_path in tqdm(json_path.glob('*.json')):
        with open(structure_path, 'r') as f:
            struct = Structure.from_dict(json.load(f))
            structures.update({structure_path.name.strip('.json'): struct})
    return structures


def read_csv(root: Path, delimiter=',', quotechar='|', newline='') -> L[D[str, str]]:
    """ reads csv to list of dicts """
    with open(root, newline=newline) as f:
        return [i for i in csv.DictReader(f, delimiter=delimiter, quotechar=quotechar)]
