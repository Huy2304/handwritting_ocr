"""
OCR Handwriting Recognition - Đọc chữ viết tay từ ảnh
"""

import cv2
import pytesseract
import os
import numpy as np
import sys

# Cấu hình đường dẫn Tesseract cho Windows (nếu cần)
if os.name == 'nt':  # Windows
    tesseract_default_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    if os.path.exists(tesseract_default_path):
        pytesseract.pytesseract.tesseract_cmd = tesseract_default_path


def preprocess_image(image_path):
    """
    Tiền xử lý ảnh để tối ưu hóa độ chính xác OCR
    """
    # Đọc ảnh
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Không thể đọc ảnh từ: {image_path}")
    
    # Phóng to ảnh để cải thiện độ chính xác với chữ nhỏ
    img = cv2.resize(img, None, fx=2.5, fy=2.5, interpolation=cv2.INTER_CUBIC)
    
    # Chuyển sang ảnh xám
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Tăng tương phản
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    gray = clahe.apply(gray)
    
    # Khử nhiễu
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    
    # Làm sắc nét ảnh (giữ dấu câu và nét chữ)
    kernel_sharp = np.array([
        [0, -1, 0],
        [-1, 5, -1],
        [0, -1, 0]
    ])
    gray = cv2.filter2D(gray, -1, kernel_sharp)
    
    # Nhị phân hóa bằng OTSU
    _, thresh = cv2.threshold(
        gray, 0, 255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )
    
    # Làm dày nét chữ nhẹ
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    
    return thresh


def extract_text(image_path, lang="vie+eng"):
    """
    Trích xuất text từ ảnh sử dụng Tesseract OCR
    
    Args:
        image_path: Đường dẫn đến file ảnh
        lang: Ngôn ngữ OCR (mặc định: tiếng Việt + tiếng Anh)
    
    Returns:
        str: Text được trích xuất từ ảnh
    """
    # Tiền xử lý ảnh
    processed_img = preprocess_image(image_path)
    
    # Cấu hình Tesseract
    custom_config = r"--oem 3 --psm 6 -c preserve_interword_spaces=1"
    
    # OCR
    text = pytesseract.image_to_string(
        processed_img,
        lang=lang,
        config=custom_config
    ).strip()
    
    return text


def main():
    """
    Hàm main - trích xuất và in text từ ảnh
    """
    # Lấy đường dẫn ảnh từ tham số dòng lệnh hoặc dùng mặc định
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        image_path = "image.png"
    
    # Kiểm tra file tồn tại
    if not os.path.exists(image_path):
        print(f"❌ Không tìm thấy ảnh: {image_path}")
        print(f"💡 Sử dụng: python main.py <đường_dẫn_ảnh>")
        sys.exit(1)
    
    try:
        # Trích xuất text
        text = extract_text(image_path)
        
        # In kết quả
        if text:
            print(text)
        else:
            print("⚠️ Không tìm thấy text trong ảnh")
            
    except Exception as e:
        print(f"❌ Lỗi: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
