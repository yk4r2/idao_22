import numpy as np
import pandas as pd
from typing import Dict as D, List as L
from pymatgen.core import Structure
from catboost import CatBoostRegressor, Pool

from models import prepare_model, MEGNetModel
from utils import read_config, read_structures


def main():
    """
    Firstly create megnet predictions on extracted defects and then 
    predicts band gap, using catboost regressor.
    """
    # ======================== Creating features using pretrained Megnet ===========================
    # get config with paths
    config: D[str, str] = read_config("config.yaml")
    # reading pymatgen structures from path
    private: D[str, Structure] = read_structures(
        config["data"]["private"]["defects"] + "pymatgen")

    # initializing model
    model: MEGNetModel = prepare_model(config["model"]["megnet"])
    # calculating predictions
    predictions: np.array = model.predict_structures(private.values())
    result: L[D[str, str]] = [{"id": id_, "predictions": pred[0]}
                              for id_, pred in zip(private.keys(), predictions)]
    megnet_predictions = pd.DataFrame(result).set_index('id')

    # ============================= Predicting band gap using boosting =============================
    data = pd.read_csv(config["data"]["private"]["features"],
                       index_col=0).merge(megnet_predictions,
                                          left_index=True,
                                          right_index=True)
    prediction_pool = Pool(data=data)
    model = CatBoostRegressor().load_model(config["model"]["boosting"])
    results = pd.DataFrame(index=data.index, columns=["predictions"])
    results["predictions"] = model.predict(prediction_pool)
    results.index.rename("id", inplace=True)
    results.to_csv("submission.csv")


if __name__ == "__main__":
    main()
