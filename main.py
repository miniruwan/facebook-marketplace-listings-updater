import asyncio
from helpers.scraper import Scraper
from helpers.google_sheet_helper import get_data_from_google_sheet, GoogleSheetWriter
from helpers.facebook_listing_helper import update_listings as update_facebook_listings
from config import config


async def main():
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
		
		# Initialize the browser
		await scraper.setup_driver()
		
		try:
			# Publish all of the vehicles into the facebook marketplace
			await update_facebook_listings(vehicle_listings, scraper, google_sheet_writer)
		finally:
			# Close the browser
			await scraper.close()


if __name__ == '__main__':
	asyncio.run(main())
