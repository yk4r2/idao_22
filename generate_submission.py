import numpy as np
import pandas as pd
from typing import Dict as D
from pymatgen.core import Structure
from catboost import CatBoostRegressor, Pool

from models import prepare_model, MEGNetModel
from utils import read_config, read_structures


def main():
    # get config with paths
    config: D[str, str] = read_config("config.yaml")
    # reading pymatgen structures from path
    private: D[str, Structure] = read_structures(config["data"]["private"]["defects"])
    # initializing model
    model: MEGNetModel = prepare_model(config["model"]["megnet"])
    # calculating predictions
    predictions: np.array = model.predict_structures(private.values())
    result = [{"id": id_, "predictions": pred[0]} for id_, pred in zip(private.keys(), predictions)]
    # saving prediction
    megnet_predictions = pd.DataFrame(result).set_index('id')

    data = pd.read_csv(config["data"]["private"]["features"], index_col=0).merge(megnet_predictions,
                                                                                 left_index=True,
                                                                                 right_index=True)
    prediction_pool = Pool(data=data)
    model = CatBoostRegressor().load_model(config["model"]["boosting"])

    predictions = model.predict(prediction_pool)
    results = pd.DataFrame(index=data.index, columns=["predictions"])
    results["predictions"] = predictions
    results.index.rename("id", inplace=True)
    results.to_csv("submission.csv")


if __name__ == "__main__":
    main()
