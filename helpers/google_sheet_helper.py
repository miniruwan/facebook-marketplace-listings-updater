import pandas as pd

ACCOUNT_NAME_COLUMN = "FB Profile"

def get_data_from_google_sheet(sheetId):
    url = f'https://docs.google.com/spreadsheets/d/{sheetId}/export?format=csv'
    df = pd.read_csv(url, skiprows=[0,1], on_bad_lines='skip',  dtype=str) # Skip first rows    
    df = df.loc[~df['Sell Price'].notna(), :] # Unsold items    
    df = pd.read_csv(url, dtype=str)
    df = df.loc[df['Refresh Facebook Advertisement?'] == 'Yes']
    return df.groupby(ACCOUNT_NAME_COLUMN)