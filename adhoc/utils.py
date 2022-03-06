from pathlib import Path
import pandas as pd
import json
from tqdm import tqdm
from pymatgen.core import Structure

tqdm.pandas()


def read_json_structures(root: Path) -> pd.DataFrame:
    return pd.DataFrame([
        {'_id': path.name.strip('.json'), 'structure': Structure.from_dict(json.load(open(path)))}
        for path in tqdm(root.glob('*.json'))
    ])


def structures_to_df(
        root_public_path=Path('../data/dichalcogenides_public'),
        root_private_path=Path('../data/dichalcogenides_private')):

    df_private = read_json_structures(root_private_path / 'structures')
    # df_public = read_json_structures(
        # root_public_path / 'structures'
    # ).merge(pd.read_csv(root_public_path / 'targets.csv'))

    # понадобится дальше
    # df_public['formula'] = df_public['structure'].apply(lambda x: x.formula)
    df_private['formula'] = df_private['structure'].apply(lambda x: x.formula)

    return df_private#, df_private


