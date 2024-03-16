import os
import time
import win32com.client 

from selenium.webdriver.chromium.webdriver import ChromiumDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from config import config

# Remove and then publish each listing
def update_listings(listings, scraper):
	# If listings are empty stop the function
	if not listings:
		return

	# Check if listing is already listed and remove it then publish it like a new one
	for listing in listings:
		print(f"_____________ {listing['Photos Folder']} _____________")
		# Remove listing if it is already published
		remove_listing(listing, scraper)

		# Publish the listing in marketplace
		publish_listing(listing, scraper)
		print(f"_____________ Done: {listing['Photos Folder']} _____________\n")

def remove_listing(data, scraper):
	title = generate_title(data)
	
	searchInput = scraper.find_element('input[placeholder="Search your listings"]', False)
	# Search input field is not existing	
	if not searchInput:
		return
	
	# Clear input field for searching listings before entering title
	scraper.element_delete_text('input[placeholder="Search your listings"]')
	# Enter the title of the listing in the input for search
	scraper.element_send_keys('input[placeholder="Search your listings"]', title.lower())
	# Search for the listing by the title
	listing_title_xpath = f'//span[text()[contains(translate(., "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"),"{title.lower()}")]]'
	listing_title = scraper.find_element_by_xpath(listing_title_xpath, False, 3)

	# Listing not found so stop the function
	if not listing_title:
		return

	print("Trying to delete ...")
	listing_title.click()

	# Click on the delete listing button
	scraper.element_click('div[aria-label="Your Listing"] div[aria-label="Delete"]')
	
	# Click on confirm button to delete
	#confirm_delete_selector = '//div[@role="dialog"]//div[@aria-label="Delete"]//span[text()]'
	#confirm_delete_selector = '//div[@role="dialog"]//div[not(@role="gridcell")]//div[@aria-label="Delete"][not(@aria-disabled)]//span[text()="Delete"]'
	confirm_delete_selector = '//div[@role="dialog"]//div[not(@role="gridcell")]/div[@aria-label="Delete"][not(@aria-disabled)]//span[text()="Delete"]'
	if scraper.find_element_by_xpath(confirm_delete_selector, False, 3):
		scraper.element_click_by_xpath(confirm_delete_selector)
	
	# Wait until the popup is closed
	scraper.element_wait_to_be_invisible('div[aria-label="Your Listing"]')
	print("Deleted.\n")

def publish_listing(data, scraper):
	print(f"Trying to add...")

	# Click on create new listing button
	scraper.element_click('div[aria-label="Marketplace sidebar"] a[aria-label="Create new listing"]')

	scraper.element_click('a[href="/marketplace/create/vehicle/"]')

	# Create string that contains all of the image paths separeted by \n
	images_path = get_image_paths(data['Photos Folder'])
	# Add images to the the listing
	scraper.input_file_add_files('input[accept="image/*,image/heif,image/heic"]', images_path)

	# Expand vehicle type select
	scraper.element_click('label[aria-label="Vehicle type"]')
	# Select vehicle type
	scraper.element_click_by_xpath('//span[text()="Car/Truck"]')

	scraper.element_send_keys('label[aria-label="Location"] input', data['Location'])
	scraper.element_click('ul[role="listbox"] li:first-child > div')

	# Scroll to years select
	scraper.scroll_to_element('label[aria-label="Year"]')
	# Expand years select
	scraper.element_click('label[aria-label="Year"]')
	scraper.element_click_by_xpath('//span[text()="' + data['Year'] + '"]')

	scraper.element_send_keys('label[aria-label="Make"] input', data['Make'])
	scraper.element_send_keys('label[aria-label="Model"] input', get_model_and_details(data))

	# Scroll to mileage input
	scraper.scroll_to_element('label[aria-label="Mileage"] input')	
	# Click on the mileage input
	scraper.element_send_keys('label[aria-label="Mileage"] input', f"{data['Kms']}000")

	scraper.element_send_keys('label[aria-label="Price"] input', data['Advertise Price'])

	# Expand body style select
	scraper.element_click('label[aria-label="Body style"]')
	# Select vehicle condition
	scraper.element_click_by_xpath('//span[text()="' + data['Body Style'] + '"]')

	if data['Clean Title'] == "Yes":
		scraper.element_click('input[aria-label="This vehicle has a clean title."]')

	# Expand vehicle condition select
	scraper.element_click('label[aria-label="Vehicle condition"]')
	# Select vehicle condition
	scraper.element_click_by_xpath('//span[text()="' + data['Vehicle Condition'] + '"]')

	# Expand fuel type select
	scraper.element_click('label[aria-label="Fuel type"]')
	# Select fuel type
	scraper.element_click_by_xpath('//span[text()="' + data['Fuel Type'] + '"]')

	# Expand transmission select
	scraper.element_click('label[aria-label="Transmission"]')
	# Select transmission
	scraper.element_click_by_xpath('//span[text()="' + data['Transmission'] + ' transmission' + '"]')
	
	scraper.element_send_keys('label[aria-label="Description"] textarea', data['Description'])

	# Wait until photos are uploaded
	driver:ChromiumDriver = scraper.driver
	WebDriverWait(driver, 60).until(
		lambda driver: len(driver.find_elements_by_xpath('//img[starts-with(@src, "data:image/gif;base64")]')) <= 1
	)

	time.sleep(5)
	next_button_selector = 'div [aria-label="Next"] > div'
	if scraper.find_element(next_button_selector, False, 3):
		scraper.element_click(next_button_selector)
		# Add listing to multiple groups
		add_listing_to_multiple_groups(scraper)

	# Publish the listing
	scraper.element_click('div[aria-label="Publish"]:not([aria-disabled])')
	scraper.element_wait_to_be_invisible('div[aria-label="Publish"]')

	print("Successfully added.")

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
def add_listing_to_multiple_groups(scraper):
	for group_name in config["facebook_group_names"]:
		# Remove whitespace before and after the name
		group_name = group_name.strip()

		scraper.element_click_by_xpath_ignore_if_not_found('//span[text()="' + group_name + '"]')

def get_model_and_details(data):
	if data['Details'] != "":
		return data['Model'] + " | " + data['Details']

	return data['Model']
