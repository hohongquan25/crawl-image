import requests
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
import time
import os
from tkinter import Tk
from tkinter.filedialog import askopenfilename, askdirectory
from PIL import Image
from io import BytesIO

# SOCKS5 proxy settings
socks5_proxy_ip = "192.168.100.199"
socks5_proxy_port = "40010"

# Function to select file with URLs
def select_file():
    Tk().withdraw()
    file_path = askopenfilename(filetypes=[("Text files", "*.txt")])
    return file_path

# Function to select folder for saving images
def select_directory():
    Tk().withdraw()
    directory_path = askdirectory(title="Select Folder to Save Images")
    return directory_path

# Modify the image URL if necessary
def modify_image_url(img_url):
    return img_url.split('?')[0]  # Loại bỏ các tham số query nếu cần

# Function to save the image in a square format
def make_square_image(img_data, output_path):
    img = Image.open(BytesIO(img_data))
    width, height = img.size
    max_dim = max(width, height)
    new_img = Image.new("RGB", (max_dim, max_dim), (255, 255, 255))
    new_img.paste(img, ((max_dim - width) // 2, (max_dim - height) // 2))
    new_img.save(output_path)
    print(f"Saved square image: {output_path}")

# Function to download image with square resizing, using proxy
def download_image(img_url, img_name, folder_name):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
        }
        # Setting up the proxy for requests
        proxies = {
            'http': f'socks5h://{socks5_proxy_ip}:{socks5_proxy_port}',
            'https': f'socks5h://{socks5_proxy_ip}:{socks5_proxy_port}'
        }

        # Make the request through the proxy
        response = requests.get(img_url, headers=headers, proxies=proxies, timeout=30)
        response.raise_for_status()

        if 'image' in response.headers['Content-Type']:
            output_path = os.path.join(folder_name, img_name)
            make_square_image(response.content, output_path)
        else:
            print(f"URL is not an image: {img_url}")

    except requests.exceptions.RequestException as e:
        print(f"Error downloading image {img_name}: {e}")

# Path to Edge WebDriver
edge_driver_path = os.path.abspath('./edgedriver_win64/msedgedriver.exe')

# Edge options with SOCKS5 proxy
edge_options = webdriver.EdgeOptions()
edge_options.add_argument(f"--proxy-server=socks5://{socks5_proxy_ip}:{socks5_proxy_port}")

# Select file with URLs
file_path = select_file()
if file_path:
    folder_name = select_directory()
    if folder_name:
        service = Service(edge_driver_path)
        driver = webdriver.Edge(service=service, options=edge_options)

        with open(file_path, 'r') as file:
            links = file.readlines()

        # Main loop for processing links
        for index, link in enumerate(links):
            link = link.strip()
            print(f"Opening link {link}")
            driver.get(link)
            time.sleep(5)  # Wait for page to load

            try:
                # Locate the parent div with class "gnvWa"
                print("Locating div with class 'gnvWa'...")
                parent_div = driver.find_element(By.CLASS_NAME, "gnvWa")

                # Find all buttons inside the parent div
                buttons = parent_div.find_elements(By.TAG_NAME, "button")
                print(f"Found {len(buttons)} button(s)")

                # Loop through each button
                for btn_index, button in enumerate(buttons):
                    try:
                        # Click the button to load content (if needed)
                        driver.execute_script("arguments[0].click();", button)
                        time.sleep(2)

                        # Locate the 'a > div > div > img' structure
                        img_element = button.find_element(By.XPATH, ".//a/div/div/img")
                        img_url = img_element.get_attribute("src")

                        print(f"Found image URL: {img_url}")

                        if img_url and img_url.startswith("http"):
                            img_url = modify_image_url(img_url)
                            img_name = f"product_{index + 1}_image_{btn_index + 1}.jpg"
                            print(f"Downloading image from URL: {img_url}")
                            download_image(img_url, img_name, folder_name)
                        else:
                            print(f"Invalid or missing image URL: {img_url}")
                    except Exception as img_error:
                        print(f"Error processing image in button {btn_index + 1}: {img_error}")

            except Exception as e:
                print(f"Error processing link {link}: {e}")

        print("Image download complete.")
        driver.quit()
    else:
        print("No folder selected.")
else:
    print("No file selected.")
