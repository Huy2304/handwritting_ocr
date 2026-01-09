# Handwriting OCR - Nhận diện chữ viết tay

Ứng dụng OCR (Optical Character Recognition) để đọc chữ viết tay từ ảnh sử dụng Tesseract OCR với tối ưu hóa cho tiếng Việt và tiếng Anh.

## 📋 Yêu cầu

- Python 3.7 trở lên
- Tesseract OCR (cần cài đặt riêng)

## 🚀 Cài đặt

### 1. Cài đặt Tesseract OCR

#### Windows:
1. Tải Tesseract từ: https://github.com/UB-Mannheim/tesseract/wiki
2. Chạy file installer và cài đặt
3. Thêm đường dẫn Tesseract vào biến môi trường PATH:
   - Mặc định: `C:\Program Files\Tesseract-OCR`
   - Hoặc chỉnh sửa trong `main.py` dòng 23 để chỉ định đường dẫn cụ thể

#### Linux (Ubuntu/Debian):
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
sudo apt-get install tesseract-ocr-vie  # Cho tiếng Việt
```

#### macOS:
```bash
brew install tesseract
brew install tesseract-lang  # Bao gồm tiếng Việt
```

### 2. Cài đặt thư viện Python

```bash
pip install -r requirements.txt
```

## 📖 Cách sử dụng

### Sử dụng ảnh mặc định (`image.png`):
```bash
python main.py
```

### Chỉ định đường dẫn ảnh:
```bash
python main.py input.jpg
python main.py path/to/your/image.png
```

## 🎯 Tính năng

- ✅ Hỗ trợ tiếng Việt và tiếng Anh
- ✅ Tối ưu hóa cho chữ viết tay và chữ in
- ✅ Tự động tiền xử lý ảnh (phóng to, tăng tương phản, khử nhiễu)
- ✅ Đơn giản, chỉ xuất text từ ảnh

## 🔧 Cấu trúc code

- `main.py`: File chính chứa các hàm OCR
  - `preprocess_image()`: Tiền xử lý ảnh
  - `extract_text()`: Trích xuất text từ ảnh
  - `main()`: Hàm chính

## 📝 Định dạng ảnh hỗ trợ

- PNG
- JPG/JPEG
- BMP
- TIFF
- Và các định dạng khác mà OpenCV hỗ trợ

## ⚙️ Tùy chỉnh

### Thay đổi ngôn ngữ OCR:
Sửa dòng trong hàm `extract_text()`:
```python
text = extract_text(image_path, lang="eng")  # Chỉ tiếng Anh
text = extract_text(image_path, lang="vie")  # Chỉ tiếng Việt
```

### Chỉ định đường dẫn Tesseract (Windows):
Uncomment và sửa dòng trong `main.py`:
```python
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
```

## 🐛 Xử lý lỗi

- **Lỗi không tìm thấy Tesseract**: Đảm bảo đã cài đặt Tesseract và thêm vào PATH
- **Lỗi không tìm thấy ngôn ngữ**: Cài đặt thêm ngôn ngữ cho Tesseract (ví dụ: `tesseract-ocr-vie` cho tiếng Việt)
- **Kết quả không chính xác**: Thử điều chỉnh tham số tiền xử lý ảnh trong hàm `preprocess_image()`

## 📄 License

MIT License
