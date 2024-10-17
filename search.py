from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import time
import re
import openpyxl
import pygame
import os

# Initialize pygame mixer
pygame.mixer.init()

# Load sound file
beep_sound = pygame.mixer.Sound("beep.wav")

# Set volume (0.0 to 1.0)
beep_sound.set_volume(0.1)  # Adjust this value to make the sound quieter

# Function to add the extension
def setup_driver_with_extension():
    # Path to the .crx file
    extension_path = os.path.join(os.getcwd(), "BusterCaptchaSolverforHumans.crx")
    
    # Set up Chrome options to include the extension
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_extension(extension_path)  # Add the extension
    
    # Initialize the WebDriver with the options
    driver = webdriver.Chrome(options=chrome_options)  # Ensure chromedriver is in PATH or provide the correct path
    return driver

# Function to get Google search results
def google_search(driver, query):
    search_results = []
    page = 0

    while True:
        url = f"https://www.google.com/search?q={query}&start={page*10}"
        driver.get(url)
        time.sleep(2)  # Allow time for the page to load

        # Check for CAPTCHA
        if "systems have detected unusual traffic from your com" in driver.page_source:
            print("CAPTCHA detected. Please resolve it to continue.")
            driver.maximize_window()  # Maximize the window when CAPTCHA is detected
            # Play sound in a loop until CAPTCHA is resolved
            while driver.current_url.startswith("https://www.google.com/sorry/"):
                # beep_sound.play(-1)  # Play sound on loop
                time.sleep(1)
                if not driver.current_url.startswith("https://www.google.com/sorry/"):
                    # beep_sound.stop()  # Stop the sound when CAPTCHA is resolved
                    driver.minimize_window()  # Minimize the window after CAPTCHA is resolved
                    break
            print("CAPTCHA resolved. Continuing with the search...")

        # Extract search result URLs
        links = driver.find_elements(By.CSS_SELECTOR, ".yuRUbf a")
        if not links:  # Exit loop if no more links are found
            break

        for link in links:
            href = link.get_attribute("href")
            if "instagram.com" in href and "/p/" not in href:
                search_results.append(href.split('?')[0])

        page += 1
        time.sleep(2)  # Pause to avoid being blocked

    return search_results

# Main function to scrape and save URLs to Excel
def scrape_instagram_urls(keywords_file):
    # Initialize the WebDriver with the extension
    driver = setup_driver_with_extension()
    driver.minimize_window()  # Minimize the window initially

    # Load search keywords from CSV
    df = pd.read_csv(keywords_file, header=None, encoding='latin1')
    keywords = df[0].tolist()

    # Load or create Excel file
    try:
        workbook = openpyxl.load_workbook("instagram_profiles.xlsx")
        sheet = workbook.active
    except FileNotFoundError:
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.append(["Profile URL"])

    # Process each keyword
    for keyword in keywords:
        print(f"Processing keyword: {keyword}")
        search_query = f'{keyword} site:instagram.com intitle:"Instagram photos and videos" -inurl:"/p/" -inurl:"/explore/" -inurl:"help.instagram.com" -inurl:"blog.instagram.com" -inurl:"/tag/"'
        search_results = google_search(driver, search_query)

        # Append new data to the Excel file
        for url in search_results:
            sheet.append([url])
        
        # Save the Excel file after each keyword
        workbook.save("instagram_profiles.xlsx")
        print(f"Data for '{keyword}' saved to instagram_profiles.xlsx")

    # Quit the browser only after all keywords are processed
    driver.quit()

# Example usage
keywords_file = 'searchKeywords.csv'
scrape_instagram_urls(keywords_file)
