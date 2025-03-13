import random
import time
import os
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Load environment variables
BOOKING_REFERENCE = os.getenv("BOOKING_REFERENCE")
LAST_NAME = os.getenv("LAST_NAME")
GHL_API_KEY = os.getenv("GHL_API_KEY")
GHL_PHONE_1 = os.getenv("GHL_PHONE_1")
GHL_PHONE_2 = os.getenv("GHL_PHONE_2")
FLIGHT_URL = os.getenv("FLIGHT_URL")

# Preferred seats to check
PREFERRED_SEATS = ["23A", "24A", "25A", "26A", "27A", "28A", "23K", "24K", "25K", "26K", "27K", "28K"]

# Setup Chrome WebDriver (headless mode)
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

def check_seat_availability():
    print("Checking Air NZ seat availability...")
    driver.get("https://flightbookings.airnewzealand.co.nz/vmanage/actions/managebookingstart")
    
    # Enter booking reference
    driver.find_element(By.NAME, "pnr").send_keys(BOOKING_REFERENCE)
    
    # Enter last name
    driver.find_element(By.NAME, "surname").send_keys(LAST_NAME, Keys.RETURN)
    
    # Wait and navigate to seat selection
    time.sleep(5)
    driver.get(FLIGHT_URL)
    time.sleep(5)
    
    # Find available seats
    available_seats = driver.find_elements(By.CLASS_NAME, "bui-SeatSelectSeat--available")
    found_seats = []
    
    for seat in available_seats:
        seat_number = seat.find_element(By.CLASS_NAME, "bui-SeatSelectSeat__seatnumber").text.strip()
        if seat_number in PREFERRED_SEATS:
            found_seats.append(seat_number)
    
    if found_seats:
        print(f"Available seats: {', '.join(found_seats)}")
        send_sms_notification(found_seats)
    else:
        print("No preferred seats available.")
    
def send_sms_notification(seats):
    message = f"Air NZ Seat Alert: Available seats on AKL -> LAX! {', '.join(seats)}. Book now!"
    
    payload = {
        "phone": GHL_PHONE_1,
        "message": message,
        "api_key": GHL_API_KEY
    }

    response1 = requests.post("https://api.yourgohighlevel.com/send_sms", json=payload)
    print(f"SMS Response for {GHL_PHONE_1}: {response1.status_code} - {response1.text}")

    payload["phone"] = GHL_PHONE_2
    response2 = requests.post("https://api.yourgohighlevel.com/send_sms", json=payload)
    print(f"SMS Response for {GHL_PHONE_2}: {response2.status_code} - {response2.text}")

    print("SMS notification attempted!")

# Main loop with random wait time
while True:
    check_seat_availability()

    random_interval = random.randint(1800, 3600)  # Random wait time between 30 to 60 minutes
    print(f"Waiting for {random_interval // 60} minutes before next check...")
    time.sleep(random_interval)
