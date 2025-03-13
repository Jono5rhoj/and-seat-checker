import os
import random
import time
import logging
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger()

# Load environment variables
BOOKING_REFERENCE = os.getenv("BOOKING_REFERENCE")
LAST_NAME = os.getenv("LAST_NAME")
GHL_API_KEY = os.getenv("GHL_API_KEY")
GHL_PHONE_1 = os.getenv("GHL_PHONE_1")
GHL_PHONE_2 = os.getenv("GHL_PHONE_2")
FLIGHT_URL = os.getenv("FLIGHT_URL")

# Preferred seats to check
PREFERRED_SEATS = ["23A", "24A", "25A", "26A", "27A", "28A", "23K", "24K", "25K", "26K", "27K", "28K"]

# Track last found seats
last_found_seats = set()

# Setup Chrome WebDriver (headless mode)
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Get Chrome binary path from environment variable or search common locations
chrome_binary = os.getenv("CHROME_BINARY_PATH")
if not chrome_binary or not os.path.exists(chrome_binary):
    possible_chrome_paths = [
        "/usr/bin/google-chrome",
        "/usr/bin/google-chrome-stable",
        "/usr/lib/chromium-browser/chrome",
        "/usr/lib/chromium/chromium",
        "/opt/google/chrome/chrome",
    ]
    for path in possible_chrome_paths:
        if os.path.exists(path):
            chrome_binary = path
            break
    if not chrome_binary:
        logger.error("No Chrome binary found in expected paths or CHROME_BINARY_PATH!")
        raise FileNotFoundError("Chrome binary not found in any known location.")

chrome_options.binary_location = chrome_binary
logger.info(f"Using Chrome binary at: {chrome_binary}")

try:
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    logger.info("Chrome WebDriver initialized successfully.")
except Exception as e:
    logger.error(f"Failed to initialize Chrome WebDriver: {e}")
    raise

def check_seat_availability():
    global last_found_seats
    logger.info("Checking Air NZ seat availability...")
    
    try:
        driver.get("https://flightbookings.airnewzealand.co.nz/vmanage/actions/managebookingstart")
        driver.find_element(By.NAME, "pnr").send_keys(BOOKING_REFERENCE)
        driver.find_element(By.NAME, "surname").send_keys(LAST_NAME, Keys.RETURN)
        WebDriverWait(driver, 10).until(EC.url_changes(driver.current_url))
        
        driver.get(FLIGHT_URL)
        available_seats = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "bui-SeatSelectSeat--available"))
        )
    except Exception as e:
        logger.error(f"Error during page navigation or loading: {e}")
        return
    
    found_seats = []
    for seat in available_seats:
        try:
            seat_number = seat.find_element(By.CLASS_NAME, "bui-SeatSelectSeat__seatnumber").text.strip()
            if seat_number in PREFERRED_SEATS:
                found_seats.append(seat_number)
        except Exception:
            continue
    
    current_seats = set(found_seats)
    if current_seats != last_found_seats:
        if found_seats:
            logger.info(f"Available seats: {', '.join(found_seats)}")
            send_sms_notification(found_seats)
        else:
            logger.info("No preferred seats available.")
        last_found_seats = current_seats
    else:
        logger.info("No change in seat availability.")

def send_sms_notification(seats):
    message = f"Air NZ Seat Alert: Available seats on AKL -> LAX! {', '.join(seats)}. Book now!"
    payload = {"message": message, "api_key": GHL_API_KEY}
    
    for phone in [GHL_PHONE_1, GHL_PHONE_2]:
        try:
            payload["phone"] = phone
            response = requests.post("https://api.yourgohighlevel.com/send_sms", json=payload, timeout=10)
            logger.info(f"SMS Response for {phone}: {response.status_code} - {response.text}")
        except Exception as e:
            logger.error(f"Failed to send SMS to {phone}: {e}")
    
    logger.info("SMS notification attempted!")

def main():
    try:
        while True:
            check_seat_availability()
            random_interval = random.randint(1800, 3600)  # 30-60 minutes
            logger.info(f"Waiting for {random_interval // 60} minutes before next check...")
            time.sleep(random_interval)
    except KeyboardInterrupt:
        logger.info("Bot stopped manually.")
    except Exception as e:
        logger.error(f"Bot crashed: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()