from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import requests

# Set up ChromeDriver service
chrome_driver_path = 'chromedriver.exe'  # Replace with the correct path to chromedriver
service = Service(chrome_driver_path)

# Your Discord user token (not email or password)
DISCORD_TOKEN = 'NDE2MjczMjQxMDI4Njg5OTMx.GwoQNP.Q1qEak54GqEEjgcO7XbQtb7qgYwA77S8jMkv_Q'

# Selenium options to keep it running in the background (headless mode)
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # Run in headless mode (no browser window)
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')

# Initialize the browser
driver = webdriver.Chrome(service=service, options=options)

def inject_token_and_login():
    """Inject the Discord user token to log in without manual credentials."""
    # Navigate to Discord's web app
    driver.get('https://discord.com/app')

    # Wait for the page to load by checking for a specific element
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    # Inject the user token into local storage
    script = f'''
    window.localStorage.setItem("token", "{DISCORD_TOKEN}");
    '''
    driver.execute_script(script)
    
    # Refresh the page after injecting the token to trigger login
    driver.refresh()
    time.sleep(5)  # Wait for Discord to load and authenticate

def download_video(url, download_path):
    """Downloads a video by navigating to the URL and simulating a download."""
    try:
        driver.get(url)
        time.sleep(3)  # Let the video load

        # Find the video element
        video_element = driver.find_element(By.TAG_NAME, 'video')

        # Extract the video source URL from the video element
        video_url = video_element.get_attribute('src')
        if video_url:
            video_name = os.path.join(download_path, url.split('/')[-1])
            print(f"Downloading video from: {video_url}")

            # Download the video using requests
            video_content = requests.get(video_url)
            with open(video_name, 'wb') as f:
                f.write(video_content.content)

            print(f"Video saved as: {video_name}")

    except Exception as e:
        print(f"Failed to download {url}: {e}")

def download_videos_from_file(file_path, download_path):
    """Read URLs from a text file and download the corresponding videos."""
    if not os.path.exists(download_path):
        os.makedirs(download_path)

    # Read all video links from the file
    with open(file_path, 'r') as file:
        video_links = file.readlines()

    for url in video_links:
        url = url.strip()  # Clean up the URL
        if url:  # Skip empty lines
            download_video(url, download_path)
            time.sleep(3)  # Small delay between downloads to avoid being flagged

# Inject the token and log in
inject_token_and_login()

# Start downloading videos
text_file_with_links = 'discord_cdn_links.txt'  # Path to your text file
download_directory = './Downloads'  # Where videos will be saved
download_videos_from_file(text_file_with_links, download_directory)

# Close the browser when done
driver.quit()
