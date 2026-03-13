import pandas as pd

def load_excel(path):

    return pd.read_excel(path)

def save_excel(df, path):

    df.to_excel(path, index=False)