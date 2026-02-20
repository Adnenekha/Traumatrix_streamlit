import json
import logging
import numpy as np
import pandas as pd
import networkx as nx
from pyvis.network import Network


def load_data_from_path(path: str) -> pd.DataFrame:
    """
    This function enables to load data from a path
    Arguments:
        path (str): string designing the path for the file
    Returns:
        DataFrame: dataframe loaded from the path
    """
    if "xlsx" in path:
        return pd.read_excel(path)

    if "csv" in path:
        encodings = ["latin1", "utf-8", "iso-8859-1", "cp1252"]

        for encoding in encodings:
            try:
                df = pd.read_csv(
                    path,
                    sep=";",
                    encoding=encoding,
                    keep_default_na=False,
                    na_values=[""],
                    low_memory=False,
                )
                return df
            except (UnicodeDecodeError, Exception) as e:
                logging.debug(f"Failed to load with encoding {encoding}: {str(e)}")
                continue

        logging.error(f"Failed to load CSV from {path} with any attempted encoding")
        return pd.DataFrame()

    else:
        logging.warning("le format de dataset est inconnu")
        return pd.DataFrame()


def process_df_dictionary(df_dict: pd.DataFrame) -> pd.DataFrame:
    """
    This function process the dictionary data frame.

    Arguments:
        df_dict (pd.Dataframe): dataframe containing the dict

    Returns:
        Dataframe: dataframe with processed columns of the dictionary
    """
    # Impute variable output name
    df_dict["output_name"] = df_dict["output_name"].fillna(df_dict["v2"])
    df_dict["output_name"] = df_dict["output_name"].fillna(df_dict["v1"])
    df_dict["output_name"] = df_dict["output_name"].fillna(df_dict["mxd"])

    # Remove whitespace from string values of dictionary
    for column_name in ["v1", "v2", "mxd", "Kill", "output_name"]:
        df_dict[column_name] = df_dict[column_name].apply(
            lambda x: x.strip() if pd.notna(x) else x
        )

    return df_dict


def filter_dataframe(df: pd.DataFrame, source: str, variable_name: str):
    """
    Filter dataframe based on variable name and source name.
    Arguments:
        df (pd.Dataframe): dataframe containing the dict
        source (string): string defining the source name
        variable_name (string): string defining the variable name

    Returns:
        Dataframe: dataframe with processed columns of the dictionary
    """
    df_source = pd.DataFrame({""})
    list_dep = []
    for var in df["output_name"]:
        if (
            df.loc[df["output_name"] == var]["parent_dependency"].isnull().values
            == False
        ):
            dep = json.loads(
                df.loc[df.output_name == var, "parent_dependency"].values[0]
            )
            if source in dep.keys():
                list_dep.append(dep[source])
            else:
                list_dep.append(None)
        else:
            list_dep.append(None)

    df_source = pd.DataFrame({"variable": df["output_name"], "dependency": list_dep})
    if variable_name == None:
        res = df_source
    else:
        res = df_source[
            df_source["dependency"].apply(
                lambda x: x is not None and variable_name in x
            )
        ]
        if res.shape[0] == 0:
            res = df_source[df_source["variable"] == variable_name]
    return res


def create_dependency_graph(df: pd.DataFrame):
    """
    Create a dependency graph from a DataFrame with variables and their dependencies.

    Parameters:
    df: DataFrame with 'variable' and 'dependency' columns
        - 'variable': variable name
        - 'dependency': list of parent variables, or None if no dependencies
    variable_name: name of the variable to treat
    """
    G = nx.DiGraph()

    # Add nodes and edges
    for _, row in df.iterrows():
        variable = row["variable"]
        dependencies = row["dependency"]

        # Add the variable as a node
        G.add_node(variable)

        # Handle dependencies
        if dependencies is not None:
            # If it's a list of dependencies
            if isinstance(dependencies, list):
                for dep in dependencies:
                    if dep is not None:
                        G.add_node(dep)
                        G.add_edge(dep, variable)
            # If it's a single dependency (not a list)
            else:
                if pd.notna(dependencies):
                    G.add_node(dependencies)
                    G.add_edge(dependencies, variable)

    # Try hierarchical layout for better visualization of dependencies
    try:
        # Use graphviz layout if available (best for hierarchical graphs)
        pos = nx.nx_agraph.graphviz_layout(G, prog="dot")
    except:
        try:
            # Fall back to hierarchical spring layout
            pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
        except:
            # Final fallback to simple spring layout
            pos = nx.spring_layout(G, seed=42)

    # Draw edges
    nx.draw_networkx_edges(
        G,
        pos,
        arrows=True,
        arrowsize=20,
        arrowstyle="->",
        width=2,
        connectionstyle="arc3,rad=0.1",
        alpha=0.6,
    )

    # Draw nodes
    nx.draw_networkx_nodes(
        G,
        pos,
        node_color="lightblue",
        node_size=3000,
        alpha=0.9,
        linewidths=2,
        edgecolors="darkblue",
    )

    # Draw labels
    nx.draw_networkx_labels(G, pos, font_size=10, font_weight="bold")

    # interactive
    nt = Network(height="700px", width="100%", directed=True)

    return G, nt
