"""
OCR Handwriting Recognition - Sử dụng VietOCR (Chính xác hơn cho tiếng Việt)
"""

import cv2
import numpy as np
import os
import sys
from PIL import Image

try:
    from vietocr.tool.predictor import Predictor
    from vietocr.tool.config import Cfg
except ImportError:
    print("❌ Chưa cài đặt VietOCR!")
    print("💡 Chạy: pip install vietocr")
    sys.exit(1)


class VietOCRProcessor:
    """Class xử lý OCR bằng VietOCR"""
    
    def __init__(self, device="cpu", beamsearch=True):
        """
        Khởi tạo VietOCR model
        
        Args:
            device: "cpu" hoặc "cuda" (nếu có GPU)
            beamsearch: Sử dụng beamsearch để tăng độ chính xác
        """
        print("🔄 Đang tải VietOCR model...")
        cfg = Cfg.load_config_from_name("vgg_transformer")
        cfg["device"] = device
        cfg["predictor"]["beamsearch"] = beamsearch
        cfg["cnn"]["pretrained"] = True
        
        self.predictor = Predictor(cfg)
        print("✅ Đã tải model thành công!")
    
    def preprocess_image(self, image_path):
        """
        Tiền xử lý ảnh để tối ưu hóa độ chính xác OCR
        
        Args:
            image_path: Đường dẫn đến file ảnh
            
        Returns:
            PIL.Image: Ảnh đã được xử lý
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
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        gray = clahe.apply(gray)
        
        # Khử nhiễu
        gray = cv2.GaussianBlur(gray, (3, 3), 0)
        
        # Nhị phân hóa bằng adaptive threshold
        binary = cv2.adaptiveThreshold(
            gray, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            31, 5
        )
        
        # VietOCR cần ảnh RGB
        rgb = cv2.cvtColor(binary, cv2.COLOR_GRAY2RGB)
        pil_img = Image.fromarray(rgb)
        
        return pil_img
    
    def extract_text(self, image_path):
        """
        Trích xuất text từ ảnh sử dụng VietOCR
        
        Args:
            image_path: Đường dẫn đến file ảnh
        
        Returns:
            str: Text được trích xuất từ ảnh
        """
        # Tiền xử lý ảnh
        processed_img = self.preprocess_image(image_path)
        
        # OCR
        text = self.predictor.predict(processed_img)
        
        return text.strip()


def main():
    """
    Hàm main - trích xuất và in text từ ảnh bằng VietOCR
    """
    # Lấy đường dẫn ảnh từ tham số dòng lệnh hoặc dùng mặc định
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        image_path = "image.png"
    
    # Kiểm tra file tồn tại
    if not os.path.exists(image_path):
        print(f"❌ Không tìm thấy ảnh: {image_path}")
        print(f"💡 Sử dụng: python main_vietocr.py <đường_dẫn_ảnh>")
        sys.exit(1)
    
    try:
        # Khởi tạo VietOCR processor
        processor = VietOCRProcessor(device="cpu", beamsearch=True)
        
        # Trích xuất text
        print(f"🔍 Đang xử lý ảnh: {image_path}...")
        text = processor.extract_text(image_path)
        
        # In kết quả
        if text:
            print("\n" + "="*50)
            print("KẾT QUẢ OCR (VietOCR):")
            print("="*50)
            print(text)
            print("="*50 + "\n")
        else:
            print("⚠️ Không tìm thấy text trong ảnh")
            
    except Exception as e:
        print(f"❌ Lỗi: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

