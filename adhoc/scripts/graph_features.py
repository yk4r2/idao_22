"""Script to calculate graph features from pymatgen-JSON files.

Usage:
    $: poetry run graph_features.py
"""
import multiprocessing as mp
from pathlib import Path

import networkx as nx
import numpy as np
import pandas as pd
from networkx import algorithms as nxalg
from pymatgen.analysis.graphs import StructureGraph
from pymatgen.analysis.local_env import CrystalNN

from adhoc.scripts.utils import structures_to_df


def _extract_features(data: pd.DataFrame) -> pd.DataFrame:
    """Calculate graph features for our pandas.DataFrame with pymatgen.core.Structure.

    Calculate such features as:
        - pagerank_min -- minimum pagerank of the nodes;
        - adamic_adar_max -- maximum adamic-adar index of the nodes;
        - num_edges -- number of edges in the graph;
        - pagerank_max -- maximum pagerank of the nodes;
        - max_formula_band_gap -- maximum band gap among the materials with the same
          formula in the train part;
        - distance_mean -- mean of structure's distance matrix;
        - density -- density characteristic from pymatgen;
        - global_efficiency -- the average global efficiency of the graph.
          The efficiency of a pair of nodes in a graph is the multiplicative inverse of
          the shortest path distance between the nodes. The average global efficiency of
          a graph is the average efficiency of all pairs of nodes.
        - degree_assortativity_coefficient -- assortativity of the graph;
          Assortativity measures the similarity of connections in the graph with respect
          to the node degree.
        - min_formula_band_gap -- minimum band gap among the materials with the same
          formula in the train part;
        - mean_formula_band_gap -- mean band gap among the materials with the same
          formula in the train part;
        - num_sites -- number of nodes in the graph;
        - pagerank_mean -- mean pagerank of the nodes;
        - adamic_adar_mean -- mean Adamic-Adar index of the nodes;
        - atomic_numbers_mean -- mean atomic number of the elements in the material;
        etc.

      ...using numpy calculations, networkx.Graph and its methods.

    Arguments:
        data :: pandas.DataFrame,
          DataFrame, which should contain structure and formula columns.

    Returns:
        pandas.DataFrame,
          DataFrame with all the graph stats calculated.
    """
    for i, _ in data.iterrows():
        structure = data.loc[i, "structure"]
        graph = nx.Graph(StructureGraph.with_local_env_strategy(structure, CrystalNN()).graph.to_undirected())
        for j in range(len(graph.nodes)):
            graph.nodes[j]["element"] = str(structure.species[j])
        data.loc[i, "atomic_numbers_min"] = np.min(structure.atomic_numbers)
        data.loc[i, "atomic_numbers_mean"] = np.mean(structure.atomic_numbers)
        data.loc[i, "atomic_numbers_max"] = np.max(structure.atomic_numbers)
        data.loc[i, "num_sites"] = structure.num_sites
        data.loc[i, "density"] = structure.density
        data.loc[i, "formula"] = structure.formula
        data.loc[i, "distance_max"] = np.max(structure.distance_matrix)
        data.loc[i, "distance_mean"] = np.mean(structure.distance_matrix)
        max_distances_matrix = np.eye(structure.num_sites) * data.loc[i, "distance_max"]
        data.loc[i, "distance_min"] = np.min(structure.distance_matrix + max_distances_matrix)

        data.loc[i, "num_edges"] = len(graph.edges)
        data.loc[i, "degree_assortativity_coefficient"] = nxalg.assortativity.degree_assortativity_coefficient(graph)
        neighbor_degrees = list(nxalg.assortativity.average_neighbor_degree(graph).values())
        data.loc[i, "neighbor_degree_min"] = np.min(neighbor_degrees)
        data.loc[i, "neighbor_degree_mean"] = np.mean(neighbor_degrees)
        data.loc[i, "neighbor_degree_max"] = np.max(neighbor_degrees)

        for elem in ["Mo", "S", "Se", "W"]:
            selected_nodes = [n for n, v in graph.nodes(data=True) if v["element"] == elem]
            if len(selected_nodes) == 0:
                data.loc[i, "neighbor_degree_min_" + elem] = 0
                data.loc[i, "neighbor_degree_mean_" + elem] = 0
                data.loc[i, "neighbor_degree_max_" + elem] = 0
                data.loc[i, "average_clustering"] = 0
                continue
            neighbor_degrees_e = list(
                nxalg.assortativity.average_neighbor_degree(graph, nodes=selected_nodes).values(),
            )
            data.loc[i, "neighbor_degree_min_" + elem] = np.min(neighbor_degrees_e)
            data.loc[i, "neighbor_degree_mean_" + elem] = np.mean(neighbor_degrees_e)
            data.loc[i, "neighbor_degree_max_" + elem] = np.max(neighbor_degrees_e)
            data.loc[i, "average_clustering"] = nxalg.cluster.average_clustering(
                graph,
                nodes=selected_nodes,
            )

        data.loc[i, "graph_clique_number"] = nxalg.clique.graph_clique_number(graph)
        data.loc[i, "average_clustering"] = nxalg.cluster.average_clustering(graph)
        data.loc[i, "diameter"] = nxalg.distance_measures.diameter(graph)
        data.loc[i, "radius"] = nxalg.distance_measures.radius(graph)
        data.loc[i, "global_efficiency"] = nxalg.efficiency_measures.global_efficiency(graph)
        data.loc[i, "local_efficiency"] = nxalg.efficiency_measures.local_efficiency(graph)
        pageranks = list(nxalg.link_analysis.pagerank(graph).values())
        data.loc[i, "pagerank_min"] = np.min(pageranks)
        data.loc[i, "pagerank_mean"] = np.mean(pageranks)
        data.loc[i, "pagerank_max"] = np.max(pageranks)
        adamic_adars = list(map(lambda x: x[2], list(nxalg.link_prediction.adamic_adar_index(graph))))
        data.loc[i, "adamic_adar_max"] = np.max(adamic_adars)
        data.loc[i, "adamic_adar_mean"] = np.mean(adamic_adars)
        data.loc[i, "s_metric"] = nxalg.s_metric(graph, normalized=False)
    return data


def extract_features(data: pd.DataFrame) -> pd.DataFrame:
    """Multithreading wrapper for _extract_features function.

    Arguments:
        data :: pandas.DataFrame,
          DataFrame, which should contain structure and formula columns.

    Returns:
        pandas.DataFrame,
          DataFrame with all the graph stats calculated.
    """
    with mp.Pool(processes=mp.cpu_count() - 1) as pool:
        results = pool.map(_extract_features, np.array_split(data, mp.cpu_count() * 4))

    results_df = pd.concat(results)

    return results_df


def append_formula_stats(data: pd.DataFrame, stats: dict) -> pd.Series:
    """Append formula stats to pandas.DataFrame.

    Arguments:
        data :: pandas.DataFrame,
          DataFrame to append stats to.
        stats :: dict,
          dict with stats for every formula.

    Returns:
        pandas.DataFrame,
          Given DataFrame with stats appended.
    """
    for i, _ in data.iterrows():
        formula = data.loc[i, "formula"]
        for name in stats:
            data.loc[i, name + "_formula_band_gap"] = stats[name].get(formula, 0)
    return data


def main() -> None:
    """Main loop for features extraction."""
    root_public_path = Path("../data/train/no_defects/pymatgen")
    root_private_path = Path("../data/eval/no_defects/pymatgen")

    df_public, df_private = structures_to_df(root_public_path, root_private_path)

    formula_statistics = dict(df_public.groupby(by="formula")["band_gap"].agg(["min", "max", "mean"]))

    df_public = extract_features(df_public)
    df_public = append_formula_stats(df_public, formula_statistics)
    df_private = extract_features(df_private)
    df_private = append_formula_stats(df_private, formula_statistics)

    df_public.drop("structure", inplace=True, axis=1)
    df_private.drop("structure", inplace=True, axis=1)

    df_public.to_csv("public.csv", index=False)
    df_private.to_csv("private.csv", index=False)


if __name__ == "__main__":
    main()
