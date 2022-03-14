from megnet.models import MEGNetModel
from megnet.data.crystal import CrystalGraph
import numpy as np
import tensorflow as tf
from pathlib import Path


def energy_within_threshold(prediction, target):
    """ calculates metrics from competition """
    success = tf.math.count_nonzero(tf.math.abs(target - prediction) < 0.02)
    return success / tf.cast(tf.size(target), tf.int64)


def _init_model(
    nfeat_bond: int = 200,
    r_cutoff: int = 20,
    gaussian_width: float = 0.5,
    npass: int = 2,
    nblocks: int = 5
) -> MEGNetModel:

    return MEGNetModel(
        graph_converter=CrystalGraph(cutoff=r_cutoff),
        centers=np.linspace(0, r_cutoff + 1, nfeat_bond),
        width=gaussian_width,
        npass=npass,
        nblocks=nblocks,
        metrics=energy_within_threshold
    )


def prepare_model(
    path: Path,
    nfeat_bond: int = 200,
    r_cutoff: int = 20,
    gaussian_width: float = 0.5,
    npass: int = 2,
    nblocks: int = 5
) -> MEGNetModel:
    """
    Initializes the model with passed parameters

    Args:
       nfeat_bond (int, optional): number of features in graph embedding. Defaults to 200.
        r_cutoff (int, optional): radius of sphere, which searches for other atoms. Defaults to 20.
        gaussian_width (float, optional): Defaults to 0.5.
        npass (int, optional): . Defaults to 2.
        nblocks (int, optional): number of megnet blocks. Defaults to 5.

    Returns:
        MEGNetModel: pretrained model
    """
    model = _init_model(nfeat_bond, r_cutoff, gaussian_width, npass, nblocks)
    model.load_weights(path)
    return model
