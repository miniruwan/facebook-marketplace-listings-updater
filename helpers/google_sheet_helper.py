import pandas as pd # Read from google sheet
import gspread # Write to google sheet

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

class GoogleSheetWriter:

    def __init__(self):
        gc = gspread.service_account()
        self.worksheet = gc.open("Cars").sheet1

    def update_flag_in_sheet(self, plateNumber:str):
        updateFacebookFlagCell = self.worksheet.find(UPDATE_FACEBOOK_YES_NO_COLUMN)
        plateNumberValueCell = self.worksheet.find(plateNumber)
        self.worksheet.update_cell(row=plateNumberValueCell.row, col=updateFacebookFlagCell.col, value="No")