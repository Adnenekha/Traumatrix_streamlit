import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import networkx as nx
import json
import os
from pyvis.network import Network
from utils import (
    load_data_from_path,
    process_df_dictionary,
)

import pandas as pd
import networkx as nx
from pyvis.network import Network
import json


path = "./"


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
                        G.add_edge(dep, variable)  # dependency -> variable
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
        edge_color="gray",
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


# Read dataset (CSV)
df = process_df_dictionary(load_data_from_path(os.path.join("./data", "dict.xlsx")))


def filter_dataframe(df: pd.DataFrame, source: str, variable_name: str):
    """ """
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
    return res


# Set header title

st.set_page_config(page_title="Traumabase", layout="wide")

st.title("Network Graph Visualization of Traumabse variables")

# Define list of selection options and sort alphabetically
variable_list = df["output_name"].to_list()

# Implement multiselect dropdown menu for option selection (returns a list)
selected_source = st.multiselect(
    "Select source to visualize", ["MEDIAXTEND", "TRAUMABASE-V1", "TRAUMABASE-V2"]
)
# Implement multiselect dropdown menu for option selection (returns a list)
selected_variable = st.multiselect("Select variable to visualize", variable_list)

# Set info message on initial site load
if len(selected_source) == 0 and len(selected_variable) in [0, 1]:
    st.text("Choose at least 1 source to start")
elif len(selected_variable) > 1:
    st.text("Choose at least 1 variable to start")
elif len(selected_source) > 1:
    st.text("Choose at least 1 variable to start")
else:
    if len(selected_variable) == 0 and len(selected_source) == 1:
        df_select = filter_dataframe(df, selected_source[0], None)
    else:
        df_select = filter_dataframe(df, selected_source[0], selected_variable[0])
    # Create networkx graph object from pandas dataframe
    G, nt = create_dependency_graph(df_select)
    nt.from_nx(G)
    nt.show("nx.html", notebook=False)

    # Save and read graph as HTML file (on Streamlit Sharing)
    try:
        nt.show(f"{path}/pyvis_graph.html", notebook=False)
        HtmlFile = open(f"{path}/pyvis_graph.html", "r", encoding="utf-8")

    # Save and read graph as HTML file (locally)
    except:
        nt.show(f"{path}/pyvis_graph.html", notebook=False)
        HtmlFile = open(f"{path}/pyvis_graph.html", "r", encoding="utf-8")

    # Load HTML file in HTML component for display on Streamlit page
    components.html(HtmlFile.read(), height=750)

# # Footer
# st.markdown(
#     """
#     <br>
#     <h6><a href="https://github.com/kennethleungty/Pyvis-Network-Graph-Streamlit" target="_blank">GitHub Repo</a></h6>
#     <h6><a href="https://kennethleungty.medium.com" target="_blank">Medium article</a></h6>
#     <h6>Disclaimer: This app is NOT intended to provide any form of medical advice or recommendations. Please consult your doctor or pharmacist for professional advice relating to any drug therapy.</h6>
#     """, unsafe_allow_html=True
#     )
