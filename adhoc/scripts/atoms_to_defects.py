"""Library to calculate Schottky-defects from pymatgen-JSON files."""
import multiprocessing as mp
from functools import partial
from pathlib import Path

import numpy as np
from pymatgen.core import Lattice, Structure
from tqdm import tqdm

from adhoc.scripts.utils import read_structures


def _diff_ideal(struct: Structure, universal_set: Structure) -> Structure:
    """Get atoms complement to our Structure (Schottky-defects).

    Arguments:
        struct :: pymatgen.core.Structure,
          Structure to get compliment for.
        universal_set :: pymatgen.core.Structure,
          Structure of a universal set, used for complement search.

    Returns:
        pymatgen.core.Structure,
          Structure created by universal_set - struct.
          For more info check pymatgen docs https://t.ly/QTem.
    """
    # defected atoms coords
    ideal_defected_atoms = tuple(universal_set - set(struct))
    defects = list(set(struct) - universal_set)

    ideal_defected_coords = np.array(
        [np.around(ideal.frac_coords, 5) for ideal in ideal_defected_atoms],
    )
    defects_coords = np.array([np.around(defect.frac_coords, 5) for defect in defects])

    for idx, ideal in enumerate(ideal_defected_coords):
        if not all(np.isin(ideal, defects_coords, True)):
            defects.append(ideal_defected_atoms[idx])

    return Structure.from_sites(defects)


def _construct_ideal() -> Structure:
    """Create an ideal molecule for Schottky-defects detection.

    Returns:
        pymatgen.core.Structure,
          Structure with the universal set, used for complement search.
    """
    coords = {
        "high": {
            "a": np.linspace(0.08333333, 0.95833333, 8, endpoint=True),
            "b": np.linspace(0.04166667, 0.91666667, 8, endpoint=True),
            "c": 0.355174,
            "element": ["S"],
            "position": [],
        },
        "mid": {
            "a": np.linspace(0.04166667, 0.91666667, 8, endpoint=True),
            "b": np.linspace(0.08333333, 0.95833333, 8, endpoint=True),
            "c": 0.25,
            "element": ["Mo"],
            "position": [],
        },
        "low": {
            "b": np.linspace(0.04166667, 0.91666667, 8, endpoint=True),
            "a": np.linspace(0.08333333, 0.95833333, 8, endpoint=True),
            "c": 0.144826,
            "element": ["S"],
            "position": [],
        },
    }

    for position in ("high", "mid", "low"):
        for a_pos in coords[position]["a"]:  # type: ignore[attr-defined]
            for b_pos in coords[position]["b"]:  # type: ignore[attr-defined]
                coords[position]["position"].append([a_pos, b_pos, coords[position]["c"]])  # type: ignore[attr-defined]

    lat = Lattice.from_parameters(25.5225256, 25.5225256, 14.879004, 90, 90, 120)

    low_element = coords["low"]["element"]
    mid_element = coords["mid"]["element"]
    high_element = coords["high"]["element"]
    elements = low_element * 64 + mid_element * 64 + high_element * 64  # type: ignore[operator]

    low_coords = coords["low"]["position"]
    mid_coords = coords["mid"]["position"]
    high_coords = coords["high"]["position"]
    positions = low_coords + mid_coords + high_coords  # type: ignore[operator]
    return Structure(lat, elements, positions, coords_are_cartesian=False)  # type: ignore[arg-type]


def extract_and_write_defects(extract_from: Path, write_to: Path, n_workers: int = 8) -> None:
    """Extracts defected atoms from structure and writes them to 
    folder in pymatgen format

    Arguments:
        extract_from :: pathlib.Path
            From where to get the whole structures

        write_to :: pathlib.Path
            Where to write defected atoms

        n_workers :: int
            Number of parallel processes to use
    """

    assert write_to.exists(), 'Destination path doesnt exist'
    assert write_to.is_dir(), 'Destination path must be a folder'
    assert extract_from.exists(), 'Extract from path must exist'
    assert extract_from.is_dir(), 'Extract from path must be a folder'
    assert len(extract_from.glob('*.json')) > 0, f'No json data found at {extract_from}'

    ideal_structure = _construct_ideal()
    ideal_set = set(ideal_structure)
    structures_dict = read_structures(extract_from)

    structures = structures_dict.values()
    ids = structures_dict.keys()

    with mp.Pool(n_workers) as p:
        result = list(
            tqdm(
                p.imap(partial(_diff_ideal, ideal_set=ideal_set), structures),
                total=len(structures),
            )
        )

    for name, item in zip(ids, result):
        with open((write_to / name).with_suffix(".json"), "w") as f:
            f.writelines(item.to_json())
