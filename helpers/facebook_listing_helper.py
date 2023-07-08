import os
import time
import win32com.client 

from config import config

# Remove and then publish each listing
def update_listings(listings, type, scraper):
	# If listings are empty stop the function
	if not listings:
		return

	# Check if listing is already listed and remove it then publish it like a new one
	for listing in listings:
		if listing['Refresh Facebook Advertisement?'] != 'Yes':
			continue

		print(f"_____________ {listing['Photos Folder']} _____________")
		# Remove listing if it is already published
		remove_listing(listing, type, scraper)

		# Publish the listing in marketplace
		publish_listing(listing, type, scraper)
		print(f"_____________ Done: {listing['Photos Folder']} _____________\n")

def remove_listing(data, listing_type, scraper):
	title = generate_title_for_listing_type(data, listing_type)
	
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
	confirm_delete_selector = 'div[aria-label="Delete listing"] div[aria-label="Delete"][tabindex="0"]'
	if scraper.find_element(confirm_delete_selector, False, 3):
		scraper.element_click(confirm_delete_selector)
	
	# Wait until the popup is closed
	scraper.element_wait_to_be_invisible('div[aria-label="Your Listing"]')
	print("Deleted.\n")

def publish_listing(data, listing_type, scraper):
	print(f"Trying to add...")

	# Click on create new listing button
	scraper.element_click('div[aria-label="Marketplace sidebar"] a[aria-label="Create new listing"]')
	# Choose listing type
	scraper.element_click('a[href="/marketplace/create/' + listing_type + '/"]')

	# Create string that contains all of the image paths separeted by \n
	images_path = get_image_paths(data['Photos Folder'])
	# Add images to the the listing
	scraper.input_file_add_files('input[accept="image/*,image/heif,image/heic"]', images_path)

	# Add specific fields based on the listing_type
	function_name = 'add_fields_for_' + listing_type
	# Call function by name dynamically
	globals()[function_name](data, scraper)
	
	scraper.element_send_keys('label[aria-label="Price"] input', data['Price'])
	scraper.element_send_keys('label[aria-label="Description"] textarea', data['Description'])
	scraper.element_send_keys('label[aria-label="Location"] input', data['Location'])
	scraper.element_click('ul[role="listbox"] li:first-child > div')

	next_button_selector = 'div [aria-label="Next"] > div'
	if scraper.find_element(next_button_selector, False, 3):
		# Go to the next step
		time.sleep(30)
		scraper.element_click(next_button_selector)
		# Add listing to multiple groups
		add_listing_to_multiple_groups(data, scraper)

	# Publish the listing
	scraper.element_click('div[aria-label="Publish"]:not([aria-disabled])')
	time.sleep(5)
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

# Add specific fields for listing from type vehicle
def add_fields_for_vehicle(data, scraper):
	# Expand vehicle type select
	scraper.element_click('label[aria-label="Vehicle type"]')
	# Select vehicle type
	#scraper.element_click_by_xpath('//span[text()="' + data['Vehicle Type'] + '"]')
	scraper.element_click_by_xpath('//span[text()="Car/Truck"]')

	# Scroll to years select
	scraper.scroll_to_element('label[aria-label="Year"]')
	# Expand years select
	scraper.element_click('label[aria-label="Year"]')
	scraper.element_click_by_xpath('//span[text()="' + data['Year'] + '"]')

	scraper.element_send_keys('label[aria-label="Make"] input', data['Make'])
	scraper.element_send_keys('label[aria-label="Model"] input', data['Model'])

	# Scroll to mileage input
	scraper.scroll_to_element('label[aria-label="Mileage"] input')	
	# Click on the mileage input
	scraper.element_send_keys('label[aria-label="Mileage"] input', data['Mileage'])

	# Expand body style select
	scraper.element_click('label[aria-label="Body style"]')
	# Select vehicle condition
	scraper.element_click_by_xpath('//span[text()="' + data['Body Style'] + '"]')

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
	scraper.element_click_by_xpath('//span[text()="' + data['Transmission'] + '"]')

	if data['Clean Title'] == "Yes":
		scraper.element_click('input[aria-label="This vehicle has a clean title."]')

# Add specific fields for listing from type item
def add_fields_for_item(data, scraper):
	scraper.element_send_keys('label[aria-label="Title"] input', data['Title'])

	# Scroll to "Category" select field
	scraper.scroll_to_element('label[aria-label="Category"]')
	# Expand category select
	scraper.element_click('label[aria-label="Category"]')
	# Select category
	scraper.element_click_by_xpath('//span[text()="' + data['Category'] + '"]')

	# Expand category select
	scraper.element_click('label[aria-label="Condition"]')
	# Select category
	scraper.element_click_by_xpath('//span[@dir="auto"][text()="' + data['Condition'] + '"]')

	if data['Category'] == 'Sports & Outdoors':
		scraper.element_send_keys('label[aria-label="Brand"] input', data['Brand'])

def generate_title_for_listing_type(data, listing_type):
	title = ''

	if listing_type == 'item':
		title = data['Title']

	if listing_type == 'vehicle':
		title = data['Year'] + ' ' + data['Make'] + ' ' + data['Model']

	return title

# Post in different groups
def add_listing_to_multiple_groups(data, scraper):
	for group_name in config["facebook_group_names"]:
		# Remove whitespace before and after the name
		group_name = group_name.strip()

		scraper.element_click_by_xpath_ignore_if_not_found('//span[text()="' + group_name + '"]')