from tqdm import tqdm
from pathlib import Path
import numpy as np
from pymatgen.core import Structure, Lattice
from utils import structures_to_df
import multiprocessing as mp
from functools import partial


def diff_ideal(s, ideal_set):

    ideal_defected_atoms = tuple(ideal_set - set(s))  # координаты молекул с проблемой
    defects = list(set(s) - ideal_set)

    ideal_defected_coords = np.array([np.around(i.frac_coords, 5) for i in ideal_defected_atoms])
    defects_coords = np.array([np.around(i.frac_coords, 5) for i in defects])

    for n, i in enumerate(ideal_defected_coords):
        if not all(np.isin(i, defects_coords, True)):
            defects.append(ideal_defected_atoms[n])

    return Structure.from_sites(defects)


def construct_ideal():
    coords = {
        'high': {
            'a': np.linspace(0.08333333, 0.95833333, 8, endpoint=True),
            'b': np.linspace(0.04166667, 0.91666667, 8, endpoint=True),
            'c': 0.355174,
            'element': ['S'],
            'position': []
        },
        'mid': {
            'a': np.linspace(0.04166667, 0.91666667, 8, endpoint=True),
            'b': np.linspace(0.08333333, 0.95833333, 8, endpoint=True),
            'c': 0.25,
            'element': ['Mo'],
            'position': []
        },
        'low': {
            'b': np.linspace(0.04166667, 0.91666667, 8, endpoint=True),
            'a': np.linspace(0.08333333, 0.95833333, 8, endpoint=True),
            'c': 0.144826,
            'element': ['S'],
            'position': []
        }
    }

    for position in ('high', 'mid', 'low'):
        for a in coords[position]['a']:
            for b in coords[position]['b']:
                coords[position]['position'].append([a, b, coords[position]['c']])

    lat = Lattice.from_parameters(25.5225256, 25.5225256, 14.879004, 90, 90, 120)
    elements = coords['low']['element'] * 64 + coords['mid']['element'] * 64 + coords['high']['element'] * 64
    positions = coords['low']['position'] + coords['mid']['position'] + coords['high']['position']

    return Structure(lat, elements,
                     positions,
                     coords_are_cartesian=False)


if __name__ == "__main__":

    ideal_structure = construct_ideal()
    ideal_set = set(ideal_structure)
    df_public = structures_to_df()
    structures = df_public['structure'].to_list()
    ids = df_public['_id'].to_list()

    with mp.Pool(8) as p:
        result = list(tqdm(p.imap(partial(diff_ideal, ideal_set=ideal_set), structures), total=len(structures)))

    path = Path('defects_private/')

    for name, item in zip(ids, result):
        with open((path / name).with_suffix('.json'), 'w') as f:
            f.writelines(item.to_json())
