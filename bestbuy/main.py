import requests
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.options import Options
import time
import os
from tkinter import Tk
from tkinter.filedialog import askopenfilename, askdirectory
from PIL import Image
from io import BytesIO

# Proxy Configuration
PROXY_IP = "192.168.100.199"  # Thay bằng địa chỉ IP proxy
PROXY_PORT = "40010"  # Thay bằng cổng proxy

# Sử dụng hộp thoại để chọn file
def select_file():
    Tk().withdraw()
    file_path = askopenfilename(filetypes=[("Text files", "*.txt")])
    return file_path

# Sử dụng hộp thoại để chọn thư mục lưu ảnh
def select_directory():
    Tk().withdraw()
    directory_path = askdirectory(title="Chọn thư mục lưu ảnh")
    return directory_path

# Hàm chỉnh sửa URL hình ảnh
def modify_image_url(img_url):
    img_url = img_url.split(';')[0]
    return f"{img_url};maxHeight=1200;maxWidth=1200;format=jpg"

def make_square_image(img_data, output_path):
    img = Image.open(BytesIO(img_data))
    width, height = img.size
    max_dim = max(width, height)
    new_img = Image.new("RGB", (max_dim, max_dim), (255, 255, 255))
    new_img.paste(img, ((max_dim - width) // 2, (max_dim - height) // 2))
    new_img.save(output_path)
    print(f"Saved square image: {output_path}")

# Updated download function with square resizing and proxy
def download_image(img_url, img_name, folder_name):
    try:
        proxies = {
            "http": f"http://{PROXY_IP}:{PROXY_PORT}",
            "https": f"http://{PROXY_IP}:{PROXY_PORT}"
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
        }
        response = requests.get(img_url, headers=headers, proxies=proxies)
        response.raise_for_status()

        if 'image' in response.headers['Content-Type']:
            output_path = os.path.join(folder_name, img_name)
            make_square_image(response.content, output_path)
        else:
            print(f"URL is not an image: {img_url}")

    except requests.exceptions.RequestException as e:
        print(f"Error downloading image {img_name}: {e}")

# Đường dẫn đến Edge WebDriver
edge_driver_path = os.path.abspath('./edgedriver_win64/msedgedriver.exe')

# Cấu hình proxy cho Selenium
edge_options = Options()
edge_options.add_argument(f"--proxy-server=http://{PROXY_IP}:{PROXY_PORT}")

# Verify if the path exists (optional)
if not os.path.exists(edge_driver_path):
    print("Edge WebDriver not found at:", edge_driver_path)
else:
    print("Using Edge WebDriver at:", edge_driver_path)

# Cho người dùng chọn file chứa link hình ảnh
file_path = select_file()
if file_path:
    folder_name = select_directory()
    if folder_name:
        service = Service(edge_driver_path)
        driver = webdriver.Edge(service=service, options=edge_options)

        with open(file_path, 'r') as file:
            links = file.readlines()

        for index, link in enumerate(links):
            link = link.strip()
            driver.get(link)
            time.sleep(5)  # Wait for the page to load

            # Kiểm tra và chọn quốc gia nếu có yêu cầu
            try:
                country_prompt = driver.find_elements(By.XPATH, "//h1[text()='Choose a country.']")
                if country_prompt:
                    us_link = driver.find_element(By.CLASS_NAME, "us-link")
                    us_link.click()  # Select US link
                    time.sleep(3)  # Wait for the page to load after country selection

                primary_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "primary-image"))
                )
                primary_button.click()

                time.sleep(2)

                li_elements = driver.find_elements(By.CSS_SELECTOR, "ol.carousel-indicate li")
                
                for li in li_elements:
                    li.click()
                    time.sleep(2)

                    img_tag = li.find_element(By.TAG_NAME, 'img')
                    if img_tag:
                        img_url = img_tag.get_attribute('src')
                        if img_url and img_url.startswith('http'):
                            img_url = modify_image_url(img_url)
                            img_name = f"product_{index + 1}_image_{li_elements.index(li) + 1}.jpg"
                            download_image(img_url, img_name, folder_name)
                        else:
                            print(f"URL không hợp lệ: {img_url}")
                    else:
                        print("Không tìm thấy hình ảnh.")

                close_button = driver.find_element(By.CSS_SELECTOR, "button.close")
                close_button.click()

            except Exception as e:
                print(f"Lỗi khi xử lý link {link}: {e}")

        print("Tải ảnh hoàn tất.")
        driver.quit()
    else:
        print("Không có thư mục nào được chọn.")
else:
    print("Không có file nào được chọn.")
