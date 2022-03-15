import numpy as np
import pandas as pd

import json
from glob import glob
from tqdm import tqdm
import collections
from pathlib import Path

import nglview
from pymatgen.core import Structure
from pymatgen.analysis.graphs import StructureGraph
from pymatgen.analysis.local_env import CrystalNN,BrunnerNN_real

import networkx as nx
from networkx.algorithms import *

from tqdm import tqdm

import multiprocessing as mp


formula_statistics = dict()

def read_json_structures(root: Path) -> pd.DataFrame:
    return pd.DataFrame([
        {'_id': path.name.strip('.json'), 'structure': Structure.from_dict(json.load(open(path)))}
        for path in tqdm(root.glob('*.json'))
    ])



def _extract_features(data):
    for i, row in data.iterrows():
        structure = data.loc[i, 'structure']
        graph = nx.Graph(StructureGraph.with_local_env_strategy(structure, CrystalNN()).graph.to_undirected())
        formula = structure.formula

        data.loc[i, 'atomic_numbers_min'] = np.min(structure.atomic_numbers)
        data.loc[i, 'atomic_numbers_mean'] = np.mean(structure.atomic_numbers)
        data.loc[i, 'atomic_numbers_max'] = np.max(structure.atomic_numbers)
        data.loc[i, 'num_sites'] = structure.num_sites
        data.loc[i, 'density'] = structure.density
        data.loc[i, 'formula'] = structure.formula
        data.loc[i, 'distance_max'] = np.max(structure.distance_matrix)
        data.loc[i, 'distance_mean'] = np.mean(structure.distance_matrix)
        data.loc[i, 'distance_min'] = np.min(structure.distance_matrix + np.eye(structure.num_sites)*data.loc[i, 'distance_max'])

        for name in formula_statistics:
            data.loc[i, name + '_formula_band_gap'] = formula_statistics[name].get(formula, 0)

        data.loc[i, 'num_edges'] = len(graph.edges)
        data.loc[i, 'degree_assortativity_coefficient'] = assortativity.degree_assortativity_coefficient(graph)
        neighbor_degrees = list(assortativity.average_neighbor_degree(graph).values())
        data.loc[i, 'neighbor_degree_min'] = np.min(neighbor_degrees)
        data.loc[i, 'neighbor_degree_mean'] = np.mean(neighbor_degrees)
        data.loc[i, 'neighbor_degree_max'] = np.max(neighbor_degrees)
        data.loc[i, 'graph_clique_number'] = clique.graph_clique_number(graph)
        data.loc[i, 'average_clustering'] = cluster.average_clustering(graph)
        data.loc[i, 'diameter'] = distance_measures.diameter(graph)
        data.loc[i, 'radius'] = distance_measures.radius(graph)
        data.loc[i, 'global_efficiency'] = efficiency_measures.global_efficiency(graph)
        data.loc[i, 'local_efficiency'] = efficiency_measures.local_efficiency(graph)
        pageranks = list(link_analysis.pagerank(graph).values())
        data.loc[i, 'pagerank_min'] = np.min(pageranks)
        data.loc[i, 'pagerank_mean'] = np.mean(pageranks)
        data.loc[i, 'pagerank_max'] = np.max(pageranks)
        adamic_adars = list(map(lambda x: x[2], list(link_prediction.adamic_adar_index(graph))))
        data.loc[i, 'adamic_adar_max'] = np.max(adamic_adars)
        data.loc[i, 'adamic_adar_mean'] = np.mean(adamic_adars)
        data.loc[i, 's_metric'] = s_metric(graph, normalized=False)

        return data

def extract_features(df):

    with mp.Pool(processes = mp.cpu_count()-1) as pool:
        results = pool.map(_extract_features, np.array_split(df, mp.cpu_count()*4))

    results_df = pd.concat(results)

    return results_df


def main():
    root_public_path = Path('../data/dichalcogenides_public')
    root_private_path = Path('../data/dichalcogenides_private')

    df_private = read_json_structures(root_private_path / 'structures')
    df_public = read_json_structures(
        root_public_path / 'structures'
    ).merge(pd.read_csv(root_public_path / 'targets.csv'))

    df_public['formula'] = df_public['structure'].apply(lambda x: x.formula)
    df_private['formula'] = df_private['structure'].apply(lambda x: x.formula)

    formula_statistics = dict(df_public.groupby(by='formula')['band_gap'].agg(['min', 'max', 'mean']))

    import time

    start = time.time()
    print("start")
    df_public = extract_features(df_public)
    df_private = extract_features(df_private)
    print("end")
    end = time.time()
    print(end - start)

    df_public.drop("structure", inplace=True, axis = 1)
    df_private.drop("structure", inplace=True, axis = 1)

    df_public.to_csv('public.csv', index=False)
    df_private.to_csv('private.csv', index=False)



if __name__ == "__main__":
    main()
