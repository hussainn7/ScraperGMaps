import time
import pandas as pd
import logging
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class RealEstateScraper:
    def __init__(self, driver_path, chrome_path, max_companies=20, search_query="Plumbing in Nashville", inactivity_timeout=30):
        self.driver_path = driver_path
        self.chrome_path = chrome_path
        self.max_companies = max_companies
        self.search_query = search_query
        self.inactivity_timeout = inactivity_timeout
        self.driver = self.setup_driver()
        self.visited_companies = set()
        self.company_count = 0
        self.data = []
        self.logger = self.setup_logger()
        self.last_activity_time = time.time()

    def setup_driver(self):
        """Initializes the WebDriver and navigates to the URL."""
        chrome_options = Options()
        chrome_options.binary_location = self.chrome_path
        service = Service(self.driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.maximize_window()
        return driver

    def setup_logger(self):
        """Sets up a logger for the program."""
        logger = logging.getLogger('RealEstateScraper')
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def navigate_to_site(self):
        """Navigate to the starting URL."""
        self.driver.get("https://www.google.com/maps")
        self.logger.info("Navigated to Google Maps.")

    def search_place(self):
        """Search for the query in Google Maps."""
        search_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "searchboxinput"))
        )
        search_input.clear()
        search_input.send_keys(self.search_query)
        submit_button = self.driver.find_element(By.ID, "searchbox-searchbutton")
        submit_button.click()
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'hfpxzc')))
        self.logger.info(f"Searching for: {self.search_query}")

    def collect_working_hours(self):
        """Collect the working hours of the company."""
        try:
            hours = self.driver.find_element(By.CLASS_NAME, 'OMl5r.hH0dDd.jBYmhd').text
        except Exception:
            hours = None
        return hours or "No working hours found"

    def collect_company_data(self):
        """Collect data from the current company page."""
        company_data = {}
        try:
            company_data['Name'] = self.driver.find_element(By.CLASS_NAME, 'DUwDvf').text
        except Exception:
            company_data['Name'] = "No name found"

        try:
            company_data['Address'] = self.driver.find_element(By.CSS_SELECTOR, '[data-item-id="address"] .Io6YTe').text
        except Exception:
            company_data['Address'] = "No address found"

        try:
            company_data['Website'] = self.driver.find_element(By.CSS_SELECTOR,
                                                             '[data-item-id="authority"] .Io6YTe').text
        except Exception:
            company_data['Website'] = "No website found"

        try:
            company_data['Phone_Number'] = self.driver.find_element(By.CSS_SELECTOR,
                                                                  '[data-item-id^="phone:tel"] .Io6YTe').text
        except Exception:
            company_data['Phone_Number'] = "No phone number found"

        company_data['Working_Hours'] = self.collect_working_hours()

        return company_data if any(value != "No" for value in company_data.values()) else None

    def handle_company_click(self, comp):
        """Handle clicking on a company and extracting data."""
        href = comp.get_attribute("href")
        if href not in self.visited_companies:
            self.visited_companies.add(href)
            try:
                WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(comp)).click()
                time.sleep(2)
                company_info = self.collect_company_data()
                if company_info:
                    self.data.append(company_info)
                    self.company_count += 1
                    self.logger.info(f"Collected data for {company_info['Name']}")

                    if self.company_count >= self.max_companies:
                        return True

                close_button = WebDriverWait(self.driver, 8).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, 'VfPpkd-icon-LgbsSe')))
                close_button.click()
                time.sleep(1)
                self.update_last_activity_time()
            except Exception as e:
                self.logger.error(f"Error handling company click: {e}")
        return False

    def update_last_activity_time(self):
        """Update the last activity time to current time."""
        self.last_activity_time = time.time()

    def check_inactivity(self):
        """Check if there has been no activity for more than the defined timeout."""
        if time.time() - self.last_activity_time > self.inactivity_timeout:
            self.logger.info(f"No activity for {self.inactivity_timeout} seconds. Stopping scraper.")
            return True
        return False

    def run(self):
        """Main function to run the scraper."""
        try:
            self.navigate_to_site()
            self.search_place()

            while self.company_count < self.max_companies:
                companies = self.driver.find_elements(By.CLASS_NAME, 'hfpxzc')

                if not companies:
                    self.logger.info("No companies found on the page")
                    if self.check_inactivity():
                        break
                    continue

                for comp in companies:
                    if self.handle_company_click(comp):
                        break

                if self.company_count >= self.max_companies:
                    break

                if self.check_inactivity():
                    break

            return self.data
        except Exception as e:
            self.logger.error(f"Error during scraping: {e}")
            raise e
        finally:
            self.driver.quit()
