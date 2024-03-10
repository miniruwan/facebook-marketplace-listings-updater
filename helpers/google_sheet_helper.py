import pandas as pd

ACCOUNT_NAME_COLUMN = "Facebook Profile"
UPDATE_FACEBOOK_YES_NO_COLUMN = "Update Facebook?"

def get_data_from_google_sheet(sheetId):
    url = f'https://docs.google.com/spreadsheets/d/{sheetId}/export?format=csv'
    df = pd.read_csv(url, skiprows=[0,1], on_bad_lines='skip',  dtype=str) # Skip first rows    
    df = df.loc[~df['Sell Price'].notna(), :] # Unsold items    
    df = df.loc[df[UPDATE_FACEBOOK_YES_NO_COLUMN] != 'No']
    df = df.loc[df[UPDATE_FACEBOOK_YES_NO_COLUMN] != '']
    df.fillna('', inplace=True)
    return df.groupby(ACCOUNT_NAME_COLUMN)