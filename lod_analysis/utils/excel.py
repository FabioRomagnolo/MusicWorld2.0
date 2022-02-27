import pandas as pd
import numpy as np
import os

EXCELS_DIRECTORY = "excels"


def save_excel(data, filename, verbose=True, get_full_info=False, evaluate=False):
    dataframe = pd.DataFrame(data)
    if get_full_info:
        filename += "_full"
    if evaluate:
        filename += "_evaluation"
    filename += ".xlsx"
    if verbose:
        print(f"Saving dataframe as {filename} ...")

    # ATTENTION! xlsxwriter Python library required to customize Excel writing!
    writer = pd.ExcelWriter(os.path.join(EXCELS_DIRECTORY, filename))
    dataframe.to_excel(writer, sheet_name=filename)
    # Adjusting columns' width according to length of words
    for column in dataframe:
        column_length = max([len(i) for i in dataframe.keys()]) + 2
        col_idx = dataframe.columns.get_loc(column)
        writer.sheets[filename].set_column(col_idx, col_idx, column_length)
    writer.save()
    # dataframe.to_excel(os.path.join(EXCELS_DIRECTORY, filename))
