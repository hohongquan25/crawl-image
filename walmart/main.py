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

# Hàm tạo ảnh vuông
def make_square_image(img_data, output_path):
    img = Image.open(BytesIO(img_data))
    width, height = img.size
    max_dim = max(width, height)
    new_img = Image.new("RGB", (max_dim, max_dim), (255, 255, 255))
    new_img.paste(img, ((max_dim - width) // 2, (max_dim - height) // 2))
    new_img.save(output_path)
    print(f"Saved square image: {output_path}")

# Hàm tải ảnh
def download_image(img_url, img_name, folder_name):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4280.88 Safari/537.36'
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

# Hàm tải ảnh từ link Walmart
def download_images_from_walmart(link, folder_name):
    service = Service(edge_driver_path)
    driver = webdriver.Edge(service=service)
    driver.get(link)
    time.sleep(5)

    try:
        # Tìm và click vào thẻ có class 'w-100 h-100 absolute top-0 left-0 white'
        click_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "w-100.h-100.absolute.top-0.left-0.white"))
        )
        click_element.click()
        time.sleep(3)  # Thời gian tải sau khi click vào

        # Tìm tất cả các thẻ div có class 'tc mb2 mr2 overflow-hidden br3 b--white ba bw1'
        div_elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "tc.mb2.mr2.overflow-hidden.br3.b--white.ba.bw1"))
        )

        # Lặp qua tất cả các thẻ div tìm ảnh
        for idx, div_element in enumerate(div_elements):
            img_tag = div_element.find_element(By.TAG_NAME, "img")
            img_url = img_tag.get_attribute('src')
            if img_url and img_url.startswith('http'):
                img_url = modify_image_url(img_url)  # Chỉnh sửa URL ảnh
                img_name = f"image_{idx + 1}.jpg"
                download_image(img_url, img_name, folder_name)
            else:
                print(f"Invalid URL: {img_url}")

    except Exception as e:
        print(f"Error processing Walmart link {link}: {e}")

    print("Image download completed.")
    driver.quit()

# Hàm giao diện nhập link
def get_input_link_for_walmart():
    def start_download():
        link = link_var.get().strip()
        if link:
            global folder_name  # Lưu thư mục để sử dụng nhiều lần
            if not folder_name:
                folder_name = select_directory()
            if folder_name:
                download_images_from_walmart(link, folder_name)
            else:
                print("No folder selected.")
        else:
            print("Please enter a link.")

    # Giao diện nhập link
    input_window = Toplevel(root)
    input_window.title("Enter Walmart Link to Download Images")

    Label(input_window, text="Enter Walmart link:").grid(row=0, column=0, padx=10, pady=10)
    Entry(input_window, textvariable=link_var, width=50).grid(row=0, column=1, padx=10, pady=10)
    Button(input_window, text="Download Images", command=start_download).grid(row=1, column=0, columnspan=2, pady=10)

# Chạy chương trình
if __name__ == "__main__":
    root = Tk()
    root.withdraw()  # Ẩn cửa sổ chính
    link_var = StringVar()
    folder_name = None  # Thư mục lưu ảnh sẽ được chọn lần đầu tiên
    get_input_link_for_walmart()
    root.mainloop()
