import time
import random
import pyperclip

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import InvalidArgumentException
from selenium.common.exceptions import ElementClickInterceptedException
import undetected as uc

from config import config

class Scraper:
	# This time is used when we are waiting for element to get loaded in the html
	wait_element_time = 90

	def __init__(self, profile_directory):
		self.profile_directory = profile_directory

		self.setup_driver_options()
		self.setup_driver()

	# Automatically close driver on destruction of the object
	def __del__(self):
		self.driver.close()

	# Add these options in order to make chrome driver appear as a human instead of detecting it as a bot
	# Also change the 'cdc_' string in the chromedriver.exe with Notepad++ for example with 'abc_' to prevent detecting it as a bot
	def setup_driver_options(self):
		self.driver_options = Options()

		arguments = [
			'--disable-blink-features=AutomationControlled',
			f"user-data-dir={config['user_data_root_folder']}",
			f"profile-directory={self.profile_directory}"
		]

		for argument in arguments:
			self.driver_options.add_argument(argument)

	# Setup chrome driver with predefined options
	def setup_driver(self):
		self.driver =  uc.Chrome(options = self.driver_options)
		self.driver.maximize_window()

	# Wait random amount of seconds before taking some action so the server won't be able to tell if you are a bot
	def wait_random_time(self):
		random_sleep_seconds = round(random.uniform(2.20, 4.20), 2)

		time.sleep(random_sleep_seconds)

	# Goes to a given page and waits random time before that to prevent detection as a bot
	def go_to_page(self, page):
		# Wait random time before refreshing the page to prevent the detection as a bot
		self.wait_random_time()
		self.driver.get(page)

	def find_element(self, selector, exit_on_missing_element = True, wait_element_time = None):
		if wait_element_time is None:
			wait_element_time = self.wait_element_time

		# Intialize the condition to wait
		wait_until = EC.element_to_be_clickable((By.CSS_SELECTOR, selector))

		try:
			# Wait for element to load
			element = WebDriverWait(self.driver, wait_element_time).until(wait_until)
		except:
			if exit_on_missing_element:
				print('ERROR: Timed out waiting for the element with css selector "' + selector + '" to load')
				# End the program execution because we cannot find the element
				exit()
			else:
				return False

		return element

	def find_element_by_xpath(self, xpath, exit_on_missing_element = True, wait_element_time = None):
		if wait_element_time is None:
			wait_element_time = self.wait_element_time

		# Intialize the condition to wait
		wait_until = EC.element_to_be_clickable((By.XPATH, xpath))

		try:
			# Wait for element to load
			element = WebDriverWait(self.driver, wait_element_time).until(wait_until)
		except:
			if exit_on_missing_element:
				# End the program execution because we cannot find the element
				print('ERROR: Timed out waiting for the element with xpath "' + xpath + '" to load')
				exit()
			else:
				return False

		return element

	# Wait random time before clicking on the element
	def element_click(self, selector, delay = True):
		if delay:
			self.wait_random_time()

		element = self.find_element(selector)

		try:
			element.click()
		except ElementClickInterceptedException:
			self.driver.execute_script("arguments[0].click();", element)

	# Wait random time before clicking on the element
	def element_click_by_xpath(self, xpath, delay = True):
		if delay:
			self.wait_random_time()

		element = self.find_element_by_xpath(xpath)

		try:
			element.click()
		except ElementClickInterceptedException:
			self.driver.execute_script("arguments[0].click();", element)

	# Wait random time before clicking on the element, and also ignore if element can't be found
	def element_click_by_xpath_ignore_if_not_found(self, xpath, delay = True):
		if delay:
			self.wait_random_time()

		element = self.find_element_by_xpath(xpath, False, 1)

		if not element:
			return # If element is not found, ignore

		try:
			element.click()
		except ElementClickInterceptedException:
			self.driver.execute_script("arguments[0].click();", element)

	# Wait random time before sending the keys to the element
	def element_send_keys(self, selector, text, delay = True):
		if delay:
			self.wait_random_time()

		element = self.find_element(selector)

		try:
			element.click()
		except ElementClickInterceptedException:
			self.driver.execute_script("arguments[0].click();", element)

		pyperclip.copy(text)
		element.send_keys(Keys.CONTROL, 'v')

	# Wait random time before sending the keys to the element
	def element_send_keys_by_xpath(self, xpath, text, delay = True):
		if delay:
			self.wait_random_time()

		element = self.find_element_by_xpath(xpath)

		try:
			element.click()
		except ElementClickInterceptedException:
			self.driver.execute_script("arguments[0].click();", element)
		
		pyperclip.copy(text)
		element.send_keys(Keys.CONTROL, 'v')

	def input_file_add_files(self, selector, files):
		# Initialize the condition to wait
		wait_until = EC.presence_of_element_located((By.CSS_SELECTOR, selector))

		try:
			# Wait for input_file to load
			input_file = WebDriverWait(self.driver, self.wait_element_time).until(wait_until)
		except:
			print('ERROR: Timed out waiting for the input_file with selector "' + selector + '" to load')
			# End the program execution because we cannot find the input_file
			exit()

		self.wait_random_time()

		try:
			input_file.send_keys(files)
		except InvalidArgumentException:
			print('ERROR: Exiting from the program! Please check if these file paths are correct:\n' + files)
			exit()

	# Wait random time before clearing the element
	def element_clear(self, selector, delay = True):
		if delay:
			self.wait_random_time()

		element = self.find_element(selector)

		element.clear()

	def element_delete_text(self, selector, delay = True):
		if delay:
			self.wait_random_time()

		element = self.find_element(selector)
		
		# Select all of the text in the input
		element.send_keys(Keys.LEFT_SHIFT + Keys.HOME)
		# Remove the selected text with backspace
		element.send_keys(Keys.BACK_SPACE)

	def element_wait_to_be_invisible(self, selector):
		wait_until = EC.invisibility_of_element_located((By.CSS_SELECTOR, selector))
		WebDriverWait(self.driver, self.wait_element_time).until(wait_until)
	
	def scroll_to_element(self, selector):
		element = self.find_element(selector)

		self.driver.execute_script('arguments[0].scrollIntoView(true);', element)

	def scroll_to_element_by_xpath(self, xpath):
		element = self.find_element_by_xpath(xpath)

		self.driver.execute_script('arguments[0].scrollIntoView(true);', element)