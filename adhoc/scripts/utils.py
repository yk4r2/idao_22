"""Utils for reading and visualizing the structures."""
import json
import warnings
from pathlib import Path, PosixPath
from typing import Optional, Tuple
from typing import Union as U

import nglview
import pandas as pd
from tqdm import tqdm

warnings.filterwarnings("ignore")
from pymatgen.core import Structure  # noqa: E402 pylint: disable=C0413

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
            raise Exception("Could not found .root file in parents dirs. Reclone repository.")
    return current_path


def _str_to_path(path: U[str, Path]) -> Path:
    path = Path(path) if isinstance(path, str) else path
    assert isinstance(path, Path)
    return path


def from_root_folder(path: U[str, Path], must_exist: bool = False) -> Path:
    """Construct path from root folder
    Examples:
        >> from_root_folder('models/ALIGNN')
           /Users/tomatoparetogmail.com/Desktop/idao_22/models/ALIGNN
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


# mypy: ignore-errors
class RootPath(PosixPath):
    """
    Allows to use paths, which are relative to root folder. Determines root path by
    looking for `.root` file. If folder containse such file, then the folder is
    considered to be root.
    Examples:
        >> path_to_data = RootPath('data')
        >> print(path_to_data)              # RootPath('/idao_2022/data)
    """

    _flavour = PosixPath._flavour

    def __new__(cls, path: U[str, Path], must_exist: bool = False):  # pylint: disable=W0221
        return super().__new__(cls, *[from_root_folder(path, must_exist)])
