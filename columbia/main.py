import requests
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from tkinter import Tk, Toplevel, Label, Entry, Button, StringVar
from PIL import Image
from io import BytesIO
from tkinter.filedialog import askdirectory

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

def download_image(img_url, img_name, folder_name):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
        }
        response = requests.get(img_url, headers=headers)
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

if not os.path.exists(edge_driver_path):
    print("Edge WebDriver not found at:", edge_driver_path)
    exit()

# Hàm chọn thư mục
def select_directory():
    return askdirectory(title="Chọn thư mục lưu ảnh")

# Hàm tải ảnh từ link
def download_images(link, folder_name):
    service = Service(edge_driver_path)
    driver = webdriver.Edge(service=service)
    driver.get(link)
    time.sleep(5)

    try:
        ul_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "ul.swiper-wrapper.list-unstyled"))
        )
        li_elements = ul_element.find_elements(By.TAG_NAME, "li")
        
        for li in li_elements:
            try:
                div_element = li.find_element(By.CLASS_NAME, "swiper-zoom-container")
                img_tag = div_element.find_element(By.TAG_NAME, "img")
                if img_tag:
                    img_url = img_tag.get_attribute('src')
                    if img_url and img_url.startswith('http'):
                        img_url = modify_image_url(img_url)
                        img_name = f"image_{li_elements.index(li) + 1}.jpg"
                        download_image(img_url, img_name, folder_name)
                    else:
                        print(f"URL không hợp lệ: {img_url}")
                else:
                    print("Không tìm thấy hình ảnh trong div.")
            except Exception as e:
                print(f"Lỗi khi xử lý thẻ li: {e}")

    except Exception as e:
        print(f"Lỗi khi xử lý link {link}: {e}")

    print("Tải ảnh hoàn tất.")
    driver.quit()

# Giao diện nhập link
def get_input_link():
    def start_download():
        link = link_var.get().strip()
        if link:
            global folder_name  # Lưu thư mục để sử dụng nhiều lần
            if not folder_name:
                folder_name = select_directory()
            if folder_name:
                download_images(link, folder_name)
            else:
                print("Không có thư mục nào được chọn.")
        else:
            print("Vui lòng nhập link.")

    # Giao diện nhập link
    input_window = Toplevel(root)
    input_window.title("Nhập link tải ảnh")

    Label(input_window, text="Nhập link:").grid(row=0, column=0, padx=10, pady=10)
    Entry(input_window, textvariable=link_var, width=50).grid(row=0, column=1, padx=10, pady=10)
    Button(input_window, text="Tải ảnh", command=start_download).grid(row=1, column=0, columnspan=2, pady=10)

# Chạy chương trình
if __name__ == "__main__":
    root = Tk()
    root.withdraw()  # Ẩn cửa sổ chính
    link_var = StringVar()
    folder_name = None  # Thư mục lưu ảnh sẽ được chọn lần đầu tiên
    get_input_link()
    root.mainloop()
