from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep, time
import pandas as pd

chrome_driver_path = r'C:\Users\Hussain\Downloads\ChromeDriver\chromedriver.exe'

chrome_options = Options()
chrome_options.binary_location = r'C:\Program Files\Google\Chrome\Application\chrome.exe'

service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

driver.get("https://www.google.com/maps/@34.1830232,-84.1515008,15z?entry=ttu&g_ep=EgoyMDI0MTAwOC4wIKXMDSoASAFQAw%3D%3D")

driver.fullscreen_window()

def search_place():
    search_input = driver.find_element(By.ID, "searchboxinput")
    search_input.send_keys("Real Estate")
    submit_button = driver.find_element(By.ID, "searchbox-searchbutton")
    submit_button.click()
    sleep(3)  

search_place()

visited_companies = set()
max_companies = 20
company_count = 0  

data = []

def scroll_down():
    """Scrolls down the page slightly to load more companies."""
    driver.execute_script("window.scrollBy(0, 250);") 
    sleep(2)  

def company():
    global company_count
    no_info_duration = 0 
    last_info_time = time() 

    while company_count < max_companies:
        companies = driver.find_elements(By.CLASS_NAME, 'hfpxzc')

        if not companies: 
            break

        for comp in companies:
            href = comp.get_attribute("href")
            if href not in visited_companies:
                visited_companies.add(href)

                try:
                    WebDriverWait(driver, 10).until(EC.element_to_be_clickable(comp))
                    comp.click()
                    sleep(5)  
                except Exception as e:
                    print(f"Could not click on {comp.text}: {e}")
                    continue 

                try:
                    name = driver.find_element(By.CLASS_NAME, 'DUwDvf').text
                except:
                    name = "No name found"

                if name in [d['Name'] for d in data]:
                    print(f"Duplicate found: {name}, skipping...")
                    close_button = driver.find_element(By.CLASS_NAME, 'VfPpkd-icon-LgbsSe')
                    close_button.click()
                    sleep(2)
                    continue

                try:
                    address = driver.find_element(By.CSS_SELECTOR, '[data-item-id="address"] .Io6YTe').text
                except:
                    address = "No address found"

                try:
                    website = driver.find_element(By.CSS_SELECTOR, '[data-item-id="authority"] .Io6YTe').text
                except:
                    website = "NO WEBSITE" 

                try:
                    phone_number = driver.find_element(By.CSS_SELECTOR, '[data-item-id^="phone:tel"] .Io6YTe').text
                except:
                    phone_number = "No phone number found"

                print(f"Name: {name}")
                print(f"Address: {address}")
                print(f"Website: {website}")
                print(f"Phone Number: {phone_number}")

                data.append({
                    "Name": name,
                    "Address": address,
                    "Website": website,
                    "Phone Number": phone_number
                })

                company_count += 1 

                last_info_time = time()

                if company_count >= max_companies: 
                    break

                try:
                    close_button = driver.find_element(By.CLASS_NAME, 'VfPpkd-icon-LgbsSe')
                    close_button.click()
                except Exception as e:
                    print(f"Could not click the close button: {e}")

                sleep(2) 
                break  

        if time() - last_info_time >= 30:  
            print("No new information for 30 seconds. Saving data...")
            save_data() 
            driver.quit()  
            return 

        scroll_down() 
        sleep(2)  

def save_data():
    df = pd.DataFrame(data)
    df.to_excel('tutoring_companies.xlsx', index=False) 
    print("Data saved to tutoring_companies.xlsx")

company()

save_data()
driver.quit()  
