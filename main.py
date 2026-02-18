from helpers.scraper import Scraper
from helpers.google_sheet_helper import get_data_from_google_sheet, GoogleSheetWriter
from helpers.facebook_listing_helper import update_listings as update_facebook_listings
from config import config


accountGroups = get_data_from_google_sheet(sheetId=config["google_sheetId"])
google_sheet_writer = GoogleSheetWriter()

for group in accountGroups:
    accountName = group[0]

    if not accountName:
        continue
    
    vehicle_listings = group[1].to_dict(orient='records')

    print("=============================================================================")
    print(f"============== Processing {len(vehicle_listings)} listings for account: {accountName} ==============")
    print("=============================================================================")

    scraper = Scraper(accountName)

    # Publish all of the vehicles into the facebook marketplace
    update_facebook_listings(vehicle_listings, scraper, google_sheet_writer)
