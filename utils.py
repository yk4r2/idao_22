import csv
import json
import yaml
from tqdm import tqdm
from pathlib import Path, PosixPath
from typing import Dict as D, List as L, Union as U, Optional

import warnings
warnings.filterwarnings("ignore")

from pymatgen.core import Structure


def read_config(path: Path) -> D[str, str]:
    """ reads config with data paths and specific options """
    with open(path, 'r') as f:
        return yaml.full_load(f)


def write_csv(data: L[D[str, str]], path: Path, fieldnames: L[str]) -> None:
    """ writes list of dicts to csv file, where each
    dict in list has same keys"""
    with open(path, 'w') as f:
        writer = csv.DictWriter(f, fieldnames)
        writer.writeheader()
        writer.writerows(data)


def read_structures(json_path: Path) -> D[str, Structure]:
    """
    takes path to the root of data and reads structures from .json file
    to dict, where keys are ids and values are pymatgen.core.Structure objects

    Args:
        root (Path): path to json data
            (for example data/train/defects/pymatgen)

    Returns:
        D[str, Structure]: dictionary of structures

    """
    json_path = Path(json_path) if isinstance(json_path, str) else json_path
    assert json_path.exists(), f'No folder exists at {json_path}'
    assert json_path.is_dir(), 'root variable must point at folder'

    structures = {}

    for structure_path in tqdm(json_path.glob('*.json')):
        with open(structure_path, 'r') as f:
            struct = Structure.from_dict(json.load(f))
            structures.update({structure_path.name.strip('.json'): struct})
    return structures


def read_csv(
    root: Path, delimiter=',', quotechar='|', newline=''
) -> L[D[str, str]]:
    """ reads csv to list of dicts """
    with open(root, newline=newline) as f:
        return [i for i in csv.DictReader(f, delimiter=delimiter,
                                          quotechar=quotechar)]


def _abs_root_path(current_path: Optional[Path] = None) -> Path:
    """detects root path by iterating from current folder upwards"""

    current_path = current_path or Path(".")
    _str_to_path(current_path)

    current_path = current_path.absolute()
    max_depth = 10

    while not (current_path / ".root").exists():
        current_path = current_path.parent
        max_depth -= 1

        if max_depth < 0:
            raise Exception("Could not found .root file in parents dirs."
                            "Reclone repository.")
    return current_path


def _str_to_path(path: U[str, Path]) -> Path:

    if isinstance(path, str):
        path = Path(path)

    assert isinstance(path, Path)
    return path


def from_root_folder(path: U[str, Path], must_exist: bool = False) -> Path:
    """Construct path from root folder
    Example:
        >> from_root_folder('models/ALIGNN')
        ... /Users/tomatoparetogmail.com/Desktop/idao_22/models/ALIGNN
    """

    path = _str_to_path(path)

    if path.is_absolute():
        raise Exception("Only relatives paths must be provided")

    root_path = _abs_root_path(path)
    absolute_path = root_path / path

    if not absolute_path.exists():
        print(f"WARNING: {absolute_path} doesnt exists")

    if must_exist and (not absolute_path.exists()):
        raise Exception(f"Constructed path {absolute_path} doesnt exist")

    return absolute_path


class RootPath(PosixPath):  # pylint: disable=C0115
    _flavour = PosixPath._flavour

    def __new__(cls, path: U[str, Path], must_exist: bool = False):
        return super().__new__(cls, *[from_root_folder(path, must_exist)])
