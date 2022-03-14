import numpy as np
from typing import Dict as D
from pymatgen.core import Structure

from models import prepare_model, MEGNetModel
from utils import read_config, read_structures, write_csv


def main():
    # get config with paths
    config: D[str, str] = read_config('config.yaml')
    # reading pymatgen structures from path
    private: D[str, Structure] = read_structures(config['data']['private']['defects'])
    # initializing model
    model: MEGNetModel = prepare_model(config['model']['weights'])
    # calculating predictions
    predictions: np.array = model.predict_structures(private.values())
    result = [{'id': id_, 'predictions': pred[0]} for id_, pred in zip(private.keys(), predictions)]
    # saving prediction
    write_csv(result, 'submission.csv', ['id', 'predictions'])


if __name__ == "__main__":
    main()
