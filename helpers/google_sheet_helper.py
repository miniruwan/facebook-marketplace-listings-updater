import csv
import os
import pandas as pd

def get_data_from_google_sheet(sheetId):
    url = f'https://docs.google.com/spreadsheets/d/{sheetId}/export?format=csv'
    df = pd.read_csv(url, dtype=str)
    records = df.to_dict(orient='records')
    return records