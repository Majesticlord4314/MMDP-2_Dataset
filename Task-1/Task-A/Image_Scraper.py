import os
import csv
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
from io import BytesIO
import time

# Define 20 Indian food subcategories
subcategories = [
    "Sydney Sweeney Hot pics"
]

images_per_category = 20  # Number of images to download per subcategory
dataset_name = "Indian_Food_Items"

if not os.path.exists(dataset_name):
    os.mkdir(dataset_name)

csv_file = os.path.join(dataset_name, "metadata.csv")
csv_f = open(csv_file, mode='w', newline='', encoding='utf-8')
csv_writer = csv.writer(csv_f)
csv_writer.writerow(["Subcategory", "Filename", "Image URL", "Resolution"])

# Setup Selenium Chrome options for Mac
chrome_options = Options()
# For debugging, temporarily remove headless mode:
# chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1080")
# Set a common user agent
chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36")

# Specify path to your ChromeDriver (update the path if needed)
service = Service("/usr/local/bin/chromedriver")
driver = webdriver.Chrome(service=service, options=chrome_options)
wait = WebDriverWait(driver, 15)  # Increased timeout for better reliability

for subcategory in subcategories:
    print(f"\nProcessing subcategory: {subcategory}...")
    subcategory_dir = os.path.join(dataset_name, subcategory.replace(" ", "_"))
    if not os.path.exists(subcategory_dir):
        os.mkdir(subcategory_dir)
    
    # Construct the search URL with "Indian food" for better relevance
    search_url = f"https://www.google.com/search?tbm=isch&q={subcategory}+Indian+food"
    driver.get(search_url)
    time.sleep(2)  # Initial wait for page load

    downloaded = 0
    image_urls = set()

    while downloaded < images_per_category:
        try:
            # Try waiting for images with the specific selector first.
            try:
                wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "img.Q4LuWd")))
                images = driver.find_elements(By.CSS_SELECTOR, "img.Q4LuWd")
            except Exception as specific_err:
                print("Specific selector not found, trying general image selector.", specific_err)
                wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "img")))
                images = driver.find_elements(By.CSS_SELECTOR, "img")
            print(f"Found {len(images)} image elements on the page.")
        except Exception as e:
            print("Error waiting for images:", e)
            break

        for img in images:
            if downloaded >= images_per_category:
                break
            try:
                # Try both "src" and "data-src"
                src = img.get_attribute("src") or img.get_attribute("data-src")
                if src and src.startswith("http") and src not in image_urls:
                    image_urls.add(src)
                    print(f"Found image URL: {src}")
                    try:
                        response = requests.get(src, timeout=10)
                        img_data = response.content
                        try:
                            image = Image.open(BytesIO(img_data))
                            resolution = f"{image.width}x{image.height}"
                        except Exception:
                            resolution = "unknown"
                        filename = f"{subcategory.replace(' ', '_')}_{downloaded+1}.jpg"
                        filepath = os.path.join(subcategory_dir, filename)
                        with open(filepath, "wb") as f:
                            f.write(img_data)
                        csv_writer.writerow([subcategory, filename, src, resolution])
                        downloaded += 1
                        print(f"Downloaded {downloaded}/{images_per_category} images for {subcategory}")
                    except Exception as download_err:
                        print(f"Error downloading image from URL {src}: {download_err}")
            except Exception as elem_err:
                print(f"Error processing an image element: {elem_err}")
        
        # Scroll down to load more images
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

csv_f.close()
driver.quit()
print("\nImage download process completed.")
