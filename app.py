# from flask import Flask, jsonify
# from flask import Flask, Response
import json
# from apscheduler.schedulers.background import BackgroundScheduler
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
# import sys
import logging
import pandas as pd
import os



log_dir = 'logs'

log_file = os.path.join(log_dir, 'scraping.log')

# Set up logging to output both to console and to a file
logging.basicConfig(
    level=logging.INFO,  # Logs everything at INFO level or higher
    format='%(asctime)s - %(levelname)s - %(message)s',  # Custom log format
    handlers=[
        logging.StreamHandler(),  # Log to console
        logging.FileHandler(log_file, mode='a', encoding='utf-8')  # Log to file (appending)
    ]
)

logger = logging.getLogger(__name__)
# sys.stdout = sys.stderr


# app = Flask(__name__)

all_products = {}

def scrape_data():
    # print("Scraping started...")
    global all_products
    # Configure Selenium WebDriver
    options = Options()
    options.add_argument("--ignore-certificate-errors")
    # options.add_argument("--start-maximized")
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    try:
        logging.info("Scraping started...")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        # print("ChromeDriver is ready!")
    except Exception as e:
        logging.error(f"Error occurred during scraping: {e}")
    
    all_products = {}
    try:
        driver.get("https://www.iranicard.ir/card/giftcard/")
        logging.info("driver read url...")
        wait = WebDriverWait(driver, 10)

        products_brand_dropdown = driver.find_element(By.XPATH, "//*[@id='block-card-block_9ea71d6d4ffff7e694494e8f3cf11fda']/div/div/div/div/div[1]/div/div/a")
        products_brand_dropdown.click()

        categories_ul = driver.find_element(By.XPATH, "//*[@id='block-card-block_9ea71d6d4ffff7e694494e8f3cf11fda']/div/div/div/div/div[1]/div/div/div/ul")
        category_li = categories_ul.find_elements(By.TAG_NAME, "li")
        logging.info("driver got categories...")

        for category in category_li:
            category_name = category.text.strip()
            if not category_name:
                continue

            category_a_tag = category.find_element(By.TAG_NAME, "a")
            try:
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable(category_a_tag)).click()
                logging.info("clicked on a tag...")
                time.sleep(2)
            except Exception:
                continue

            card_values_a_tag = WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
                (By.XPATH, "//*[@id='block-card-block_9ea71d6d4ffff7e694494e8f3cf11fda']/div/div/div/div/div[3]/div/div/a")
            ))
            card_values_a_tag.click()
            time.sleep(1)

            card_values_ul = driver.find_element(By.XPATH, "//*[@id='block-card-block_9ea71d6d4ffff7e694494e8f3cf11fda']/div/div/div/div/div[3]/div/div/div/ul")
            li_elements = card_values_ul.find_elements(By.TAG_NAME, "li")

            category_products = []

            for li in li_elements:
                a_tag = li.find_element(By.TAG_NAME, "a")
                item_dict = {
                    "category": category_name,
                    "data-currency": a_tag.get_attribute("data-currency"),
                    "data-price_currency": a_tag.get_attribute("data-price_currency"),
                    "data-price_rial": a_tag.get_attribute("data-price_rial"),
                    "product_text": a_tag.text.strip() or f"{a_tag.get_attribute('data-price_currency')} {a_tag.get_attribute('data-currency')}"
                }
                category_products.append(item_dict)

            all_products[category_name] = category_products
            card_values_a_tag.click()
            time.sleep(1)
            products_brand_dropdown.click()
        
        logging.info(f"Scraping completed! Found data for {len(all_products)} categories.")
        # print("data scrape completed")
    finally:
        driver.quit()

    try:
        df = pd.DataFrame(all_products)
        df.to_excel('scraped_data.xlsx', index=False, encoding='utf-8')
        logging.info("Data saved to scraped_data.xlsx")
    except Exception as e:
        logging.error(f"Error saving data to Excel file: {e}")

    return all_products

scrape_data()
# Schedule daily scraping
# scheduler = BackgroundScheduler()
# scheduler.add_job(scrape_data, 'cron', hour=11, minute=14, max_instances=1)  # Adjust time as needed
# scheduler.start()


# @app.route('/api/products', methods=['GET'])
# def get_products():
#     # data = scrape_data()
#     # response = json.dumps(data, ensure_ascii=False, indent=4)
#     # return Response(response, content_type="application/json; charset=utf-8")
#     global all_products
    
#     if not all_products:
#         logger.info("No data available yet.")  # استفاده از logging
#         return Response(json.dumps({"error": "Data not available. Try later."}), 
#                         content_type="application/json; charset=utf-8", 
#                         status=503)
#     response = json.dumps(all_products, ensure_ascii=False, indent=4)
#     logger.info("Data available.")  # استفاده از logging
#     return Response(response, content_type="application/json; charset=utf-8")
# if __name__ == "__main__":
#     try:
#         logger.info("scrape_data() start doing some amazing thing for you!.")  # استفاده از logging
#         scrape_data()
#     except Exception as e:
#         logger.info("scrape_data() didn't start.")  # استفاده از logging
#     scrape_data()
#     app.run(debug=True)
