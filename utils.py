import json
import logging
from functools import reduce
from typing import Set, Tuple

import numpy as np
import pandas as pd


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