from helpers.scraper import Scraper
from helpers.google_sheet_helper import get_data_from_google_sheet
from helpers.facebook_listing_helper import update_listings as update_facebook_listings
from config import config

accountGroups = get_data_from_google_sheet(sheetId=config["google_sheetId"])
for group in accountGroups:
    accountName = group[0]
    vehicle_listings = group[1].to_dict(orient='records')

    scraper = Scraper('https://facebook.com')

    # Add login functionality to the scraper
    scraper.add_login_functionality('https://facebook.com', 'svg[aria-label="Your profile"]', accountName)

    scraper.go_to_page('https://facebook.com/marketplace/you/selling')

    # Publish all of the vehicles into the facebook marketplace
    update_facebook_listings(vehicle_listings, 'vehicle', scraper)
