import pandas as pd

ACCOUNT_NAME_COLUMN = "A"

def get_data_from_google_sheet(sheetId):
    url = f'https://docs.google.com/spreadsheets/d/{sheetId}/export?format=csv'
    df = pd.read_csv(url, dtype=str)
    df = df.loc[df['Refresh Facebook Advertisement?'] == 'Yes']
    return df.groupby(ACCOUNT_NAME_COLUMN)