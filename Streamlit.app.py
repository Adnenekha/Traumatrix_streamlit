import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import os
from pyvis.network import Network
from utils import (
    load_data_from_path,
    process_df_dictionary,
    create_dependency_graph,
    filter_dataframe,
)

path = "./"


# Read dict dataset
df = process_df_dictionary(load_data_from_path(os.path.join("./data", "dict.xlsx")))

# Set header title

st.set_page_config(page_title="Traumabase", layout="wide")

st.title("Network Graph Visualization of Traumabse variables")


# Define list of selection options and sort alphabetically
variable_list = df["output_name"].to_list()

# Select which source to use
selected_source = st.multiselect(
    "Select source to visualize",
    ["MEDIAXTEND", "TRAUMABASE-V1", "TRAUMABASE-V2"],
    max_selections=1,
)

# Select all or one variable:
all_source = st.multiselect(
    "Select to visualize all variables ofthe source or not",
    ["Yes", "No"],
    max_selections=1,
)

# Implement multiselect dropdown menu for option selection (returns a list)
selected_variable = st.multiselect("Select variable to visualize", variable_list)


# Set info message on initial site load
if len(selected_source) == 0 and len(selected_variable) == 0 and len(all_source) == 0:
    st.text("Choose at least 1 source to start")
elif len(selected_source) == 0 and (
    len(selected_variable) != 0 or len(all_source) != 0
):
    st.text("Choose at least 1 source to start")
elif len(selected_source) == 1 and len(all_source) == 0:
    st.text("Choose to visualize one variable or all")
elif (
    len(selected_source) == 1 and len(selected_variable) == 0 and all_source[0] == "No"
):
    st.text("Choose at least 1 variable to start")
else:
    if len(selected_source) == 1 and all_source[0] == "Yes":
        df_select = filter_dataframe(df, selected_source[0], None)
    else:
        df_select = pd.DataFrame()
        for var in selected_variable:
            df_select_temp = filter_dataframe(df, selected_source[0], var)
            df_select = pd.concat([df_select, df_select_temp])
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
