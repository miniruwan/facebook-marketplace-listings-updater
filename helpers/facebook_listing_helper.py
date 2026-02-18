import os
import time
import asyncio
import win32com.client 

from helpers.scraper import Scraper
from helpers.google_sheet_helper import GoogleSheetWriter
from config import config

# Remove and then publish each listing
async def update_listings(listings, scraper:Scraper, google_sheet_writer: GoogleSheetWriter):

	await scraper.go_to_page('https://facebook.com/marketplace/you/selling')

	# Check if listing is already listed and remove it then publish it like a new one
	for listing in listings:
		print(f"_____________ {listing['Photos Folder']} _____________")
		# Remove listing if it is already published
		await remove_listing(listing, scraper)

		# Publish the listing in marketplace
		await publish_listing(listing, scraper)
		google_sheet_writer.update_flag_in_sheet(listing["Plate Number"])
		print(f"_____________ Done: {listing['Photos Folder']} _____________\n")

async def remove_listing(data, scraper:Scraper):
	title = generate_title(data)
	
	searchInput = await scraper.find_element('input[placeholder="Search your listings"]', False)
	# Search input field is not existing	
	if not searchInput:
		return
	
	# Clear input field for searching listings before entering title
	await scraper.element_delete_text('input[placeholder="Search your listings"]')
	# Enter the title of the listing in the input for search
	await scraper.element_send_keys('input[placeholder="Search your listings"]', title.lower())

	# Search for the listing by the title
	listing_title_xpath = f'//span[text()[contains(translate(., "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"),"{title.lower()}")]]'
	listing_title = await scraper.find_element_by_xpath(listing_title_xpath, False, 15)

	# Listing not found so stop the function
	if not listing_title:
		return

	print("🧹 Trying to delete ...")

	await listing_title.click()

	# Click on the delete listing button
	await scraper.element_click_by_xpath('//div[@aria-label="Delete marketplace listing"]')
	
	# Click on confirm button to delete
	confirm_delete_selector = '(//div[@role="dialog"]//span[text()="Delete"])[last()]'
	await scraper.element_click_by_xpath(confirm_delete_selector)

	# Wait until the popup is closed
	await scraper.element_wait_to_be_invisible('div[aria-label="Your Listing"]')

	print("✅ Deleted.\n")

async def publish_listing(data, scraper:Scraper):
	print(f"➕ Trying to add...")

	await scraper.go_to_page("https://www.facebook.com/marketplace/create/vehicle")

	# Create string that contains all the image paths separated by \n
	images_path = get_image_paths(data['Photos Folder'])
	# Add images to the listing
	await scraper.input_file_add_files('input[accept="image/*,image/heif,image/heic"]', images_path)

	await select_vehicle_type(scraper)

	await scraper.element_send_keys_by_xpath('//span[contains(text(),"Location")]/following-sibling::input', data["Location"])
	await scraper.element_click('ul[role="listbox"] li:first-child > div')

	await scraper.element_click_by_xpath("//span[contains(text(),'Year')]")
	await scraper.element_click_by_xpath('//span[text()="' + data['Year'] + '"]')

	make_element_xpath = '//span[contains(text(),"Make")]/following-sibling::input'
	await scraper.scroll_to_element_by_xpath(make_element_xpath)
	await scraper.element_send_keys_by_xpath(make_element_xpath, data['Make'])

	model_element_xpath = '//span[contains(text(),"Model")]/following-sibling::input'
	await scraper.scroll_to_element_by_xpath(model_element_xpath)
	await scraper.element_send_keys_by_xpath(model_element_xpath, get_model_and_details(data))

	await scraper.element_send_keys_by_xpath('//span[contains(text(),"Mileage")]/following-sibling::input', f"{data['Kms']}000")

	await scraper.element_send_keys_by_xpath('//span[contains(text(),"Price")]/following-sibling::input', data["Advertise Price"])

	# Expand body style select
	body_style_xpath = "//span[contains(text(),'Body style')]"
	await scraper.scroll_to_element_by_xpath(body_style_xpath)
	await scraper.element_click_by_xpath(body_style_xpath)
	await scraper.element_click_by_xpath_ignore_if_not_found('//span[text()="' + data['Body Style'] + '"]')

	# Select vehicle condition
	if data['Clean Title'] == "Yes":
		await scraper.element_click('input[aria-label="This vehicle has a clean title."]')

	# Expand vehicle condition select
	vehicle_condition_xpath = "//span[contains(text(),'Vehicle condition')]"
	await scraper.scroll_to_element_by_xpath(vehicle_condition_xpath)
	await scraper.element_click_by_xpath(vehicle_condition_xpath)
	# Select vehicle condition
	await scraper.element_click_by_xpath('//span[text()="' + data['Vehicle Condition'] + '"]')

	# Expand fuel type select
	fuel_type_xpath = "//span[contains(text(),'Fuel type')]"
	await scraper.scroll_to_element_by_xpath(fuel_type_xpath)
	await scraper.element_click_by_xpath(fuel_type_xpath)
	# Select fuel type
	await scraper.element_click_by_xpath('//span[text()="' + data['Fuel Type'] + '"]')

	# Expand transmission select
	transmission_xpath = "//span[contains(text(),'Transmission')]"
	await scraper.scroll_to_element_by_xpath(transmission_xpath)
	await scraper.element_click_by_xpath(transmission_xpath)
	# Select transmission
	await scraper.element_click_by_xpath('//span[text()="' + data['Transmission'] + ' transmission' + '"]')

	description_element_xpath = '//span[contains(text(),"Description")]/..//textarea'
	await scraper.scroll_to_element_by_xpath(description_element_xpath)
	await scraper.element_send_keys_by_xpath(description_element_xpath, data['Description'])

	# Wait until photos are uploaded - check for loading gif images
	timeout = 60
	start_time = time.time()
	while time.time() - start_time < timeout:
		try:
			elements = await scraper.tab.xpath('//img[starts-with(@src, "data:image/gif;base64")]')
			if len(elements) <= 1:
				break
		except:
			break
		await asyncio.sleep(1)

	await asyncio.sleep(25)
	next_button_selector = 'div [aria-label="Next"] > div'
	if await scraper.find_element(next_button_selector, False, 3):
		await scraper.element_click(next_button_selector)
		# Add listing to multiple groups
		# await add_listing_to_multiple_groups(scraper)

	# Publish the listing
	await asyncio.sleep(15)
	await do_final_publishing(data, scraper)

async def do_final_publishing(data, scraper:Scraper):
	await scraper.element_click('div[aria-label="Publish"]:not([aria-disabled])')
	try:
		await scraper.element_wait_to_be_invisible('div[aria-label="Publish"]')
	except Exception as e:
		handledError = await handle_final_publishing_error(data, scraper)

		if handledError:
			print("💪 Successfully handled \"Something went wrong\" error.")
			return

		print(f'😔 Failed to add: {repr(e)}')
		return

	print("🎉 Successfully added.")


async def handle_final_publishing_error(data, scraper:Scraper):

	if not await scraper.find_element_by_xpath('//span[text()="Something went wrong"]', False, 1):
		return False

	print("\n🤞 Got \"Something went wrong\" message from facebook. Trying to delete and re-publish...")

	await scraper.element_click_by_xpath('//span[text()="Close"]')

	original_tab = scraper.tab
	# Open new tab
	new_tab = await scraper.browser.get("https://www.facebook.com/marketplace/you/selling", new_tab=True)
	# Temporarily switch scraper to use new tab
	scraper.tab = new_tab
	await remove_listing(data, scraper)
	await new_tab.close()
	# Switch back to original tab
	scraper.tab = original_tab
	await original_tab.activate()

	await do_final_publishing(data, scraper)
	return True


def get_image_paths(photosSubFolder):
	shell = win32com.client.Dispatch("WScript.Shell")

	paths = []
	# Eg: C:\Users\MiniruwanMangala\OneDrive\Pictures\cars\Toyota Echo\Facebook
	folderPath = os.path.join(config["photos_root_folder"], photosSubFolder, config["facebook_photos_sub_folder_name"])
	if os.path.exists(folderPath):
		links = [os.path.join(folderPath, fn) for fn in next(os.walk(folderPath))[2]]
		paths = [(shell.CreateShortCut(link)).Targetpath for link in links]
	else:
		# Eg: C:\Users\MiniruwanMangala\OneDrive\Pictures\cars\Toyota Echo
		folderPath = os.path.dirname(folderPath)
		paths = [os.path.join(folderPath, fn) for fn in next(os.walk(folderPath))[2]]
	
	paths = [ path for path in paths if not path.endswith(".txt") ]

	return '\n'.join(paths)


def generate_title(data):
	return data['Year'] + ' ' + data['Make'] + ' ' + get_model_and_details(data)

# Post in different groups
async def add_listing_to_multiple_groups(scraper:Scraper):
	for group_name in config["facebook_group_names"]:
		# Remove whitespace before and after the name
		group_name = group_name.strip()

		await scraper.element_click_by_xpath_ignore_if_not_found('//span[text()="' + group_name + '"]')

def get_model_and_details(data):
	if data['Details'] != "":
		return data['Model'] + " | " + data['Details']

	return data['Model']

async def select_vehicle_type(scraper:Scraper):
	await scraper.element_click_by_xpath("//span[contains(text(),'Vehicle type')]")
	await scraper.element_click_by_xpath_ignore_if_not_found("//span[contains(text(),'Car/Truck')]")
	await scraper.element_click_by_xpath_ignore_if_not_found("//span[contains(text(),'Car/van')]")