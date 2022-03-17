"""Utils for reading and visualizing the structures."""
import json
from pathlib import Path
from typing import Tuple

import nglview
import pandas as pd
from pymatgen.core import Structure
from tqdm import tqdm

tqdm.pandas()


def read_json_structures(root: Path) -> pd.DataFrame:
    """JSON -> pymatgen.core.Structure converter.

    Arguments:
        root :: pathlib.Path,
          Path to your structures' root. By default, two folders in `data/`.

    Returns:
        pandas.DataFrame,
          DataFrame wrapping pymatgen.core.Structure with "_id" and "structure"-columns.
    """
    return pd.DataFrame(
        [
            {
                "_id": path.name.strip(".json"),
                "structure": Structure.from_dict(json.load(open(path))),
            }
            for path in tqdm(root.glob("*.json"))
        ]
    )


# pylint: disable=syntax-error
def structures_to_df(
    root_public_path: Path = Path("../data/dichalcogenides_public"),
    root_private_path: Path = Path("../data/dichalcogenides_private"),
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Wrap pymatgen-structures to pandas.DataFrame.

    Arguments:
        root_public_path :: pathlib.Path,
          Path to public pymatgen jsons. By default, in data -> dichalcogenides_public.
        root_private_path :: pathlib.Path,
          Path to private pymatgen jsons. By default, in data -> dichalcogenides_public.

    Returns:
        Tuple of two pandas.DataFrames.
          df_public contains structure, formula and targets columns.
          df_private contains structure and formula only.
    """
    df_private = read_json_structures(root_private_path)
    df_public = read_json_structures(root_public_path).merge(pd.read_csv(root_public_path / "targets.csv"))

    # may be used in the future
    df_public["formula"] = df_public["structure"].apply(lambda x: x.formula)
    df_private["formula"] = df_private["structure"].apply(lambda x: x.formula)

    return df_public, df_private


def show(struct: Structure) -> None:
    """Plot pymatgen atomic grid structure.

    Arguments:
        struct :: pymatgen.core.Structure,
          Pymatgen-like structure. [More info](https://t.ly/QTem)
    """
    nglview.show_pymatgen(struct)
