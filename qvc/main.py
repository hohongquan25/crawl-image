import requests
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from tkinter import Tk
from tkinter.filedialog import askopenfilename, askdirectory
from PIL import Image
from io import BytesIO

# Sử dụng hộp thoại để chọn file
def select_file():
    Tk().withdraw()  # Ẩn cửa sổ gốc của Tkinter
    file_path = askopenfilename(filetypes=[("Text files", "*.txt")])
    return file_path

# Sử dụng hộp thoại để chọn thư mục lưu ảnh
def select_directory():
    Tk().withdraw()  # Ẩn cửa sổ gốc của Tkinter
    directory_path = askdirectory(title="Chọn thư mục lưu ảnh")
    return directory_path

# Hàm để làm cho ảnh thành hình vuông mà không mất nội dung
def make_square_image(img_data, output_path):
    # Open the image
    img = Image.open(BytesIO(img_data))
    
    # Get dimensions
    width, height = img.size
    max_dim = max(width, height)
    
    # Create a new square image with a white background
    new_img = Image.new("RGB", (max_dim, max_dim), (255, 255, 255))
    
    # Paste the original image onto the center of the new square image
    new_img.paste(img, ((max_dim - width) // 2, (max_dim - height) // 2))
    
    # Save the new square image
    new_img.save(output_path)
    print(f"Saved square image: {output_path}")

# Hàm tải ảnh từ URL với đường dẫn thư mục và làm cho nó thành hình vuông
def download_image2(img_url, img_name, folder_name): 
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
        }
        response = requests.get(img_url, headers=headers)
        response.raise_for_status()  # Kiểm tra lỗi HTTP

        # Kiểm tra xem nội dung có phải là hình ảnh không
        if 'image' not in response.headers['Content-Type']:
            print(f"Lỗi: URL {img_url} không phải là hình ảnh.")
            return

        # Save the image as a square image with padding
        output_path = os.path.join(folder_name, img_name)
        make_square_image(response.content, output_path)

    except requests.exceptions.RequestException as e:
        print(f"Lỗi khi tải ảnh {img_name}: {e}")

# Đường dẫn đến Edge WebDriver
edge_driver_path = os.path.abspath('./edgedriver_win64/msedgedriver.exe')

# Verify if the path exists (optional)
if not os.path.exists(edge_driver_path):
    print("Edge WebDriver not found at:", edge_driver_path)
else:
    print("Using Edge WebDriver at:", edge_driver_path)

# Cho người dùng chọn file chứa link hình ảnh
file_path = select_file()
if file_path:  # Kiểm tra nếu người dùng đã chọn file
    # Cho người dùng chọn thư mục lưu hình ảnh
    folder_name = select_directory()
    if folder_name:  # Kiểm tra nếu người dùng đã chọn thư mục
        # Khởi tạo Selenium Edge WebDriver
        service = Service(edge_driver_path)
        driver = webdriver.Edge(service=service)

        with open(file_path, 'r') as file:
            links = file.readlines()

        for index, link in enumerate(links):
            link = link.strip()
            driver.get(link)
            time.sleep(5)  # Chờ trang tải hoàn toàn (điều chỉnh nếu cần)

            try:
                # Tìm thẻ div có class là "imageList"
                image_list_div = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "imageList"))
                )
                
                # Tìm tất cả các thẻ <a> trong thẻ div đó
                image_links = image_list_div.find_elements(By.TAG_NAME, 'a')
                
                for img_link in image_links:
                    img_url = img_link.get_attribute('href')  # Lấy URL của hình ảnh
                    if img_url and img_url.startswith('http'):
                        img_name = f"product_{index + 1}_image_{image_links.index(img_link) + 1}.jpg"
                        download_image2(img_url, img_name, folder_name)  # Gọi hàm với đường dẫn thư mục
                    else:
                        print(f"URL không hợp lệ: {img_url}")

            except Exception as e:
                print(f"Lỗi khi xử lý link {link}: {e}")

        print("Tải ảnh hoàn tất.")
        
        # Đóng trình duyệt
        driver.quit()
    else:
        print("Không có thư mục nào được chọn.")
else:
    print("Không có file nào được chọn.")