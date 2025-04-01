import time
import pandas as pd
import logging
import sys
import atexit
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class RealEstateScraper:
    def __init__(self, driver_path, max_companies=20, output_file='Business.xlsx', inactivity_timeout=30):
        self.driver_path = driver_path
        self.max_companies = max_companies
        self.output_file = output_file
        self.inactivity_timeout = inactivity_timeout  # Timeout for inactivity
        self.driver = self.setup_driver()
        self.visited_companies = set()
        self.company_count = 0
        self.data = []
        self.logger = self.setup_logger()
        self.last_activity_time = time.time() 

    def setup_driver(self):
        """Initializes the WebDriver and navigates to the URL."""
        chrome_options = Options()
        chrome_options.binary_location = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
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
        self.driver.get(
            "https://www.google.com/maps/@40.4975771,-98.2373288,5.86z?entry=ttu&g_ep=EgoyMDI1MDMyNS4xIKXMDSoASAFQAw%3D%3D")
        self.logger.info("Navigated to Google Maps.")

    def search_place(self):
        """Search for Real Estate in Google Maps."""
        search_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "searchboxinput"))
        )
        search_input.clear()
        search_input.send_keys("Plumbing in Nashville")
        submit_button = self.driver.find_element(By.ID, "searchbox-searchbutton")
        submit_button.click()
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'hfpxzc')))
        self.logger.info("Searching for real estate companies.")

    def scroll_left_list(self):
        """Scroll the left-hand list of companies."""
        try:
            scrollable_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'section-scrollbox'))
            )
            self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_element)
            time.sleep(1)
            self.logger.info("Scrolled the company list.")
            self.update_last_activity_time()
        except Exception as e:
            self.logger.error(f"Error scrolling the left-hand list: {e}")

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
            company_data['Phone Number'] = self.driver.find_element(By.CSS_SELECTOR,
                                                                    '[data-item-id^="phone:tel"] .Io6YTe').text
        except Exception:
            company_data['Phone Number'] = "No phone number found"

        company_data['Working Hours'] = self.collect_working_hours()

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
            self.logger.info(f"No activity for {self.inactivity_timeout} seconds. Saving data and exiting.")
            self.save_data()
            self.driver.quit()
            sys.exit(0)

    def save_data(self):
        """Save the collected data to an Excel file."""
        if self.data:
            df = pd.DataFrame(self.data)
            df.to_excel(self.output_file, index=False)
            self.logger.info(f"Data saved to {self.output_file}")
        else:
            self.logger.warning("No data to save.")

    def graceful_exit(self, signal, frame):
        """Handle graceful exit when interrupted or Chrome is closed."""
        self.logger.info("Program interrupted or Chrome closed. Saving data...")
        self.save_data()
        self.driver.quit()
        sys.exit(0)

    def run(self):
        """Main function to run the scraper."""
        self.navigate_to_site()
        self.search_place()

        while self.company_count < self.max_companies:
            companies = self.driver.find_elements(By.CLASS_NAME, 'hfpxzc')

            if not companies:
                self.logger.info("No companies found on the page, scrolling...")
                self.check_inactivity() 
                continue

            for comp in companies:
                if self.handle_company_click(comp):
                    break

            if self.company_count >= self.max_companies:
                break

            self.check_inactivity()  

        self.save_data()
        self.driver.quit()


if __name__ == "__main__":
    scraper = RealEstateScraper(driver_path=r'C:\Users\Syedh\Downloads\ChromeDriver\chromedriver.exe', max_companies=12)
    scraper.run()