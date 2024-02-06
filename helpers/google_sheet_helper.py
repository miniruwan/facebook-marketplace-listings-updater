import pandas as pd

ACCOUNT_NAME_COLUMN = "Facebook Profile"

def get_data_from_google_sheet(sheetId):
    url = f'https://docs.google.com/spreadsheets/d/{sheetId}/export?format=csv'
    df = pd.read_csv(url, skiprows=[0,1], on_bad_lines='skip',  dtype=str) # Skip first rows    
    df = df.loc[~df['Sell Price'].notna(), :] # Unsold items    
    df = df.loc[df[ACCOUNT_NAME_COLUMN] != 'None']
    df = df.loc[df[ACCOUNT_NAME_COLUMN] != '']
    df.fillna('', inplace=True)
    return df.groupby(ACCOUNT_NAME_COLUMN)