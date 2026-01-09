# Handwriting OCR - Nhận diện chữ viết tay

Ứng dụng OCR (Optical Character Recognition) để đọc chữ viết tay từ ảnh với nhiều phương pháp:
- **Tesseract OCR**: Phương pháp truyền thống, nhanh, hỗ trợ nhiều ngôn ngữ
- **VietOCR**: Mô hình deep learning, chính xác hơn cho tiếng Việt

Hỗ trợ cả giao diện dòng lệnh và giao diện đồ họa (GUI).

## 📋 Yêu cầu

- Python 3.7 trở lên
- Tesseract OCR (cần cài đặt riêng) - cho Tesseract OCR
- PyTorch - tự động cài khi cài đặt VietOCR

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

### 1. Giao diện đồ họa (GUI) - Khuyến nghị ⭐

Giao diện trực quan, dễ sử dụng, hỗ trợ cả Tesseract và VietOCR:

```bash
python main_gui.py
```

**Tính năng GUI:**
- ✅ Chọn ảnh bằng file dialog
- ✅ Xem trước ảnh trước khi xử lý
- ✅ Chọn phương pháp OCR (Tesseract hoặc VietOCR)
- ✅ Chọn ngôn ngữ (cho Tesseract)
- ✅ Hiển thị kết quả với khả năng sao chép
- ✅ Lưu kết quả ra file text

### 2. Dòng lệnh với Tesseract OCR

Sử dụng ảnh mặc định (`image.png`):
```bash
python main.py
```

Chỉ định đường dẫn ảnh:
```bash
python main.py input.jpg
python main.py path/to/your/image.png
```

### 3. Dòng lệnh với VietOCR (Chính xác hơn cho tiếng Việt)

```bash
python main_vietocr.py
python main_vietocr.py input.jpg
```

**Lưu ý:** Lần đầu chạy VietOCR sẽ tải model (có thể mất vài phút).

## 🎯 Tính năng

- ✅ **Giao diện đồ họa (GUI)**: Dễ sử dụng, trực quan
- ✅ **Nhiều phương pháp OCR**: Tesseract OCR và VietOCR
- ✅ **Hỗ trợ đa ngôn ngữ**: Tiếng Việt, tiếng Anh
- ✅ **Tối ưu hóa cho chữ viết tay**: Tự động tiền xử lý ảnh (phóng to, tăng tương phản, khử nhiễu)
- ✅ **Xem trước ảnh**: Hiển thị ảnh trước khi xử lý
- ✅ **Xuất kết quả**: Sao chép hoặc lưu file text
- ✅ **Xử lý đa luồng**: Không làm đơ giao diện khi xử lý

## 🔧 Cấu trúc code

### Files chính:

- **`main.py`**: File dòng lệnh sử dụng Tesseract OCR
  - `preprocess_image()`: Tiền xử lý ảnh
  - `extract_text()`: Trích xuất text từ ảnh
  - `main()`: Hàm chính

- **`main_vietocr.py`**: File dòng lệnh sử dụng VietOCR (chính xác hơn)
  - `VietOCRProcessor`: Class xử lý OCR bằng VietOCR
  - `preprocess_image()`: Tiền xử lý ảnh cho VietOCR
  - `extract_text()`: Trích xuất text với VietOCR

- **`main_gui.py`**: Giao diện đồ họa (GUI)
  - `OCRApp`: Class quản lý giao diện
  - Hỗ trợ cả Tesseract và VietOCR
  - Xem trước ảnh, xử lý đa luồng, xuất kết quả

- **`vietocr.py`**: File gốc sử dụng VietOCR (tham khảo)

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

### Tesseract OCR:
- **Lỗi không tìm thấy Tesseract**: Đảm bảo đã cài đặt Tesseract và thêm vào PATH
- **Lỗi không tìm thấy ngôn ngữ**: Cài đặt thêm ngôn ngữ cho Tesseract (ví dụ: `tesseract-ocr-vie` cho tiếng Việt)
- **Kết quả không chính xác**: Thử điều chỉnh tham số tiền xử lý ảnh trong hàm `preprocess_image()`

### VietOCR:
- **Lỗi ImportError**: Chạy `pip install vietocr` để cài đặt
- **Lỗi tải model chậm**: Lần đầu chạy sẽ tự động tải model từ internet, vui lòng đợi
- **Lỗi CUDA/GPU**: Nếu có GPU, có thể chỉnh `device="cuda"` trong `main_vietocr.py` để tăng tốc
- **Model chưa sẵn sàng trong GUI**: Đợi vài giây để model tải xong, thanh trạng thái sẽ hiển thị

### Chung:
- **Ảnh quá lớn/nhỏ**: Ứng dụng tự động xử lý, nhưng ảnh chất lượng tốt sẽ cho kết quả chính xác hơn
- **Chữ quá nhỏ hoặc mờ**: Thử chỉnh độ tương phản ảnh trước khi xử lý

## 📄 License

MIT License
