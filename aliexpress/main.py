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
    Tk().withdraw()
    return askopenfilename(filetypes=[("Text files", "*.txt")])

# Sử dụng hộp thoại để chọn thư mục lưu ảnh
def select_directory():
    Tk().withdraw()
    return askdirectory(title="Chọn thư mục lưu ảnh")

# Làm ảnh thành hình vuông mà không mất nội dung
def make_square_image(img_data, output_path):
    try:
        img = Image.open(BytesIO(img_data))
        width, height = img.size
        max_dim = max(width, height)
        new_img = Image.new("RGB", (max_dim, max_dim), (255, 255, 255))
        new_img.paste(img, ((max_dim - width) // 2, (max_dim - height) // 2))
        new_img.save(output_path, "JPEG")
        print(f"Saved square image: {output_path}")
    except Exception as e:
        print(f"Error processing image: {e}")

# Tải ảnh từ URL và xử lý định dạng .avif
def download_image(img_url, img_name, folder_name):
    try:
        # Kiểm tra nếu URL có đuôi .avif, loại bỏ .avif và đổi tên thành .jpg
        if '.avif' in img_url:
            img_url = img_url.replace('.avif', '.jpg')  # Chuyển đổi thành định dạng .jpg
            img_name = os.path.splitext(img_name)[0] + '.jpg'  # Đổi tên file thành .jpg
            print(f"Đã chuyển đổi ảnh từ .avif sang .jpg: {img_url}")
        
        # Thay thế '80x80' hoặc '220x220' bằng '800x800' trong URL
        img_url = img_url.replace("80x80", "800x800").replace("220x220", "800x800")

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
        }
        response = requests.get(img_url, headers=headers, timeout=10)
        response.raise_for_status()

        # Lưu ảnh nếu hợp lệ
        output_path = os.path.join(folder_name, img_name)
        img_data = response.content

        make_square_image(img_data, output_path)

    except requests.exceptions.RequestException as e:
        print(f"Lỗi khi tải ảnh {img_name}: {e}")
    except Exception as e:
        print(f"Lỗi không xác định khi xử lý ảnh {img_name}: {e}")

# Đường dẫn đến Edge WebDriver
edge_driver_path = os.path.abspath('./edgedriver_win64/msedgedriver.exe')

def main():
    # Lựa chọn file và thư mục lưu
    file_path = select_file()
    if not file_path:
        print("Không có file nào được chọn.")
        return

    folder_name = select_directory()
    if not folder_name:
        print("Không có thư mục nào được chọn.")
        return

    try:
        service = Service(edge_driver_path)
        driver = webdriver.Edge(service=service)

        with open(file_path, 'r') as file:
            links = file.readlines()

        for index, link in enumerate(links):
            link = link.strip()
            driver.get(link)
            print("Vui lòng xác thực nếu cần (chờ 30 giây)...")
            time.sleep(30)  # Chờ bạn xác thực thủ công nếu cần

            try:
                # Tìm thẻ div chứa slider
                slider_div = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "slider--slider--uRpGJpg"))
                )
                # Tìm tất cả các thẻ div con chứa ảnh
                image_divs = slider_div.find_elements(By.CLASS_NAME, "slider--img--K0YbWW2")
                
                for img_index, image_div in enumerate(image_divs):
                    try:
                        # Tìm thẻ img trong từng thẻ div
                        img_tag = image_div.find_element(By.TAG_NAME, "img")
                        img_url = img_tag.get_attribute("src")
                        if img_url and img_url.startswith("http"):
                            img_name = f"product_{index + 1}_image_{img_index + 1}.jpg"
                            print(f"Tải ảnh từ URL: {img_url}")
                            download_image(img_url, img_name, folder_name)
                        else:
                            print(f"URL không hợp lệ hoặc không tìm thấy: {img_url}")
                    except Exception as img_error:
                        print(f"Lỗi khi xử lý ảnh {img_index + 1}: {img_error}")
            except Exception as e:
                print(f"Lỗi khi xử lý link {link}: {e}")

        print("Tải ảnh hoàn tất.")
    except Exception as driver_error:
        print(f"Lỗi khi khởi tạo trình duyệt: {driver_error}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
