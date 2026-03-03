import time
import random
import asyncio
import pyperclip

import zendriver as zd
from zendriver.core.keys import SpecialKeys, KeyModifiers, KeyEvents

from config import config

class Scraper:
	# This time is used when we are waiting for element to get loaded in the html
	wait_element_time = 90

	def __init__(self, profile_directory):
		self.profile_directory = profile_directory
		self.browser = None
		self.tab = None

	# Initialize browser asynchronously
	async def setup_driver(self):
		# Configure zendriver
		user_data_dir = f"{config['user_data_root_folder']}\\{self.profile_directory}"
		
		self.browser = await zd.start(
			user_data_dir=user_data_dir,
			headless=False
		)
		
		# Get the first tab
		self.tab = self.browser.main_tab
		await self.tab.maximize()

	# Automatically close driver on destruction of the object
	async def close(self):
		if self.browser:
			await self.browser.stop()

	# Wait random amount of seconds before taking some action so the server won't be able to tell if you are a bot
	async def wait_random_time(self):
		random_sleep_seconds = round(random.uniform(2.20, 4.20), 2)
		await asyncio.sleep(random_sleep_seconds)

	# Goes to a given page and waits random time before that to prevent detection as a bot
	async def go_to_page(self, page):
		# Wait random time before refreshing the page to prevent the detection as a bot
		await self.wait_random_time()
		await self.tab.get(page)

	async def find_element(self, selector, exit_on_missing_element = True, wait_element_time = None):
		if wait_element_time is None:
			wait_element_time = self.wait_element_time

		try:
			# Wait for element to load
			element = await self.tab.select(selector, timeout=wait_element_time)
			return element
		except Exception as e:
			if exit_on_missing_element:
				print('ERROR: Timed out waiting for the element with css selector "' + selector + '" to load')
				# End the program execution because we cannot find the element
				exit()
			else:
				return False

	async def find_element_by_xpath(self, xpath, exit_on_missing_element = True, wait_element_time = None):
		if wait_element_time is None:
			wait_element_time = self.wait_element_time

		try:
			# Wait for element to load
			elements = await self.tab.xpath(xpath, timeout=wait_element_time)
			if elements:
				return elements[0]
			else:
				raise Exception("Element not found")
		except Exception as e:
			if exit_on_missing_element:
				# End the program execution because we cannot find the element
				print('ERROR: Timed out waiting for the element with xpath "' + xpath + '" to load')
				exit()
			else:
				return False

	# Wait random time before clicking on the element
	async def element_click(self, selector, delay = True):
		if delay:
			await self.wait_random_time()

		element = await self.find_element(selector)
		await element.click()

	# Wait random time before clicking on the element
	async def element_click_by_xpath(self, xpath, delay = True):
		if delay:
			await self.wait_random_time()

		element = await self.find_element_by_xpath(xpath)
		await element.scroll_into_view()
		# Wait for element to settle after scrolling
		await asyncio.sleep(0.5)
		
		# Retry clicking if position can't be found
		max_retries = 3
		for attempt in range(max_retries):
			try:
				await element.click()
				break
			except Exception as e:
				if "could not find position" in str(e) and attempt < max_retries - 1:
					print(f"Position not found, retrying click ({attempt + 1}/{max_retries})...")
					await asyncio.sleep(0.5)
				else:
					raise

	# Wait random time before clicking on the element, and also ignore if element can't be found
	async def element_click_by_xpath_ignore_if_not_found(self, xpath, delay = True):
		if delay:
			await self.wait_random_time()

		element = await self.find_element_by_xpath(xpath, False, 1)

		if not element:
			return # If element is not found, ignore

		try:
			await element.scroll_into_view()
			# Wait for element to settle after scrolling
			await asyncio.sleep(0.5)
			
			# Retry clicking if position can't be found
			max_retries = 3
			for attempt in range(max_retries):
				try:
					await element.click()
					break
				except Exception as e:
					if "could not find position" in str(e) and attempt < max_retries - 1:
						await asyncio.sleep(0.5)
					else:
						raise
		except Exception:
			# Element was found but couldn't be clicked (not visible, position not found, etc.)
			# Since this method should ignore failures, we just return
			return

	# Wait random time before sending the keys to the element
	async def element_send_keys(self, selector, text, delay = True):
		if delay:
			await self.wait_random_time()

		element = await self.find_element(selector)
		await element.click()
		
		pyperclip.copy(text)
		# Simulate Ctrl+V
		ctrl_v_events = KeyEvents.from_mixed_input([("v", KeyModifiers.Ctrl)])
		await element.send_keys(ctrl_v_events)

	# Wait random time before sending the keys to the element
	async def element_send_keys_by_xpath(self, xpath, text, delay = True):
		if delay:
			await self.wait_random_time()

		element = await self.find_element_by_xpath(xpath)
		await element.scroll_into_view()
		await element.click()
		
		pyperclip.copy(text)
		# Simulate Ctrl+V
		ctrl_v_events = KeyEvents.from_mixed_input([("v", KeyModifiers.Ctrl)])
		await element.send_keys(ctrl_v_events)

	async def input_file_add_files(self, selector, files):
		try:
			# Wait for input_file to load
			input_file = await self.tab.select(selector, timeout=self.wait_element_time)
		except:
			print('ERROR: Timed out waiting for the input_file with selector "' + selector + '" to load')
			# End the program execution because we cannot find the input_file
			exit()

		await self.wait_random_time()

		try:
			# Convert newline-separated paths to list
			file_paths = files.split('\n')
			await input_file.send_file(*file_paths)
		except Exception as e:
			print('ERROR: Exiting from the program! Please check if these file paths are correct:\n' + files)
			print('Error details:', str(e))
			exit()

	# Wait random time before clearing the element
	async def element_clear(self, selector, delay = True):
		if delay:
			await self.wait_random_time()

		element = await self.find_element(selector)
		await element.clear_input()

	async def element_delete_text(self, selector, delay = True):
		if delay:
			await self.wait_random_time()

		element = await self.find_element(selector)
		
		# Clear the input using zendriver's method
		await element.clear_input()

	async def element_wait_to_be_invisible(self, selector):
		# In zendriver, we can check if element still exists
		timeout = self.wait_element_time
		start_time = time.time()
		
		while time.time() - start_time < timeout:
			try:
				elem = await self.tab.select(selector, timeout=1)
				if not elem:
					return
			except:
				return
			await asyncio.sleep(0.5)
	
	async def scroll_to_element(self, selector):
		element = await self.find_element(selector)
		await element.scroll_into_view()

	async def scroll_to_element_by_xpath(self, xpath):
		element = await self.find_element_by_xpath(xpath)
		await element.scroll_into_view()