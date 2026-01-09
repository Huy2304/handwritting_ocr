"""
OCR Handwriting Recognition - Giao diện ứng dụng
Hỗ trợ cả Tesseract OCR và VietOCR
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import sys
from PIL import Image, ImageTk
import threading
import cv2
import numpy as np

# Import các module OCR
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

try:
    from vietocr.tool.predictor import Predictor
    from vietocr.tool.config import Cfg
    VIETOCR_AVAILABLE = True
except ImportError:
    VIETOCR_AVAILABLE = False

# Cấu hình đường dẫn Tesseract cho Windows
if sys.platform == 'win32':
    tesseract_default_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    if os.path.exists(tesseract_default_path) and TESSERACT_AVAILABLE:
        pytesseract.pytesseract.tesseract_cmd = tesseract_default_path


class OCRApp:
    """Giao diện ứng dụng OCR"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("OCR Handwriting Recognition")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        self.image_path = None
        self.original_image = None
        self.display_image = None
        self.vietocr_processor = None
        
        self.setup_ui()
        self.load_vietocr_model()
    
    def setup_ui(self):
        """Thiết lập giao diện người dùng"""
        
        # Frame chính
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Cấu hình grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # === Phần chọn file ===
        file_frame = ttk.LabelFrame(main_frame, text="Chọn ảnh", padding="10")
        file_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)
        
        ttk.Button(file_frame, text="Chọn ảnh...", command=self.select_image).grid(row=0, column=0, padx=(0, 10))
        
        self.file_label = ttk.Label(file_frame, text="Chưa chọn ảnh", foreground="gray")
        self.file_label.grid(row=0, column=1, sticky=tk.W)
        
        # === Phần hiển thị ảnh ===
        image_frame = ttk.LabelFrame(main_frame, text="Xem trước ảnh", padding="10")
        image_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        image_frame.columnconfigure(0, weight=1)
        image_frame.rowconfigure(0, weight=1)
        
        self.image_label = ttk.Label(image_frame, text="Chưa có ảnh", anchor=tk.CENTER)
        self.image_label.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # === Phần cấu hình OCR ===
        config_frame = ttk.LabelFrame(main_frame, text="Cấu hình OCR", padding="10")
        config_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Chọn phương pháp OCR
        ttk.Label(config_frame, text="Phương pháp OCR:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.ocr_method = tk.StringVar(value="tesseract")
        methods = []
        if TESSERACT_AVAILABLE:
            methods.append(("Tesseract OCR", "tesseract"))
        if VIETOCR_AVAILABLE:
            methods.append(("VietOCR (Chính xác hơn)", "vietocr"))
        
        if not methods:
            methods.append(("Không có OCR nào khả dụng", "none"))
            self.ocr_method.set("none")
        
        for text, value in methods:
            ttk.Radiobutton(config_frame, text=text, variable=self.ocr_method, 
                          value=value).grid(row=1, column=0, sticky=tk.W, pady=2)
        
        # Ngôn ngữ (chỉ cho Tesseract)
        ttk.Label(config_frame, text="Ngôn ngữ:").grid(row=2, column=0, sticky=tk.W, pady=(10, 5))
        self.lang_var = tk.StringVar(value="vie+eng")
        lang_frame = ttk.Frame(config_frame)
        lang_frame.grid(row=3, column=0, sticky=tk.W)
        
        ttk.Radiobutton(lang_frame, text="Tiếng Việt + Anh", variable=self.lang_var, 
                       value="vie+eng").grid(row=0, column=0, sticky=tk.W)
        ttk.Radiobutton(lang_frame, text="Chỉ tiếng Việt", variable=self.lang_var, 
                       value="vie").grid(row=1, column=0, sticky=tk.W)
        ttk.Radiobutton(lang_frame, text="Chỉ tiếng Anh", variable=self.lang_var, 
                       value="eng").grid(row=2, column=0, sticky=tk.W)
        
        # Nút chạy OCR
        run_button = ttk.Button(config_frame, text="🔍 Chạy OCR", command=self.run_ocr)
        run_button.grid(row=4, column=0, pady=(20, 0), sticky=(tk.W, tk.E))
        
        # === Phần kết quả ===
        result_frame = ttk.LabelFrame(main_frame, text="Kết quả OCR", padding="10")
        result_frame.grid(row=2, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)
        
        # Text area với scrollbar
        self.result_text = scrolledtext.ScrolledText(result_frame, wrap=tk.WORD, 
                                                     width=40, height=20, font=("Arial", 11))
        self.result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Nút sao chép kết quả
        button_frame = ttk.Frame(result_frame)
        button_frame.grid(row=1, column=0, pady=(10, 0), sticky=(tk.W, tk.E))
        
        ttk.Button(button_frame, text="📋 Sao chép", command=self.copy_result).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(button_frame, text="💾 Lưu kết quả", command=self.save_result).grid(row=0, column=1)
        
        # === Thanh trạng thái ===
        self.status_var = tk.StringVar(value="Sẵn sàng")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def load_vietocr_model(self):
        """Tải VietOCR model trong background"""
        if not VIETOCR_AVAILABLE:
            return
        
        def load_model():
            try:
                self.status_var.set("Đang tải VietOCR model...")
                cfg = Cfg.load_config_from_name("vgg_transformer")
                cfg["device"] = "cpu"
                cfg["predictor"]["beamsearch"] = True
                cfg["cnn"]["pretrained"] = True
                self.vietocr_processor = Predictor(cfg)
                self.status_var.set("VietOCR model đã sẵn sàng!")
            except Exception as e:
                self.status_var.set(f"Lỗi tải VietOCR: {str(e)}")
        
        thread = threading.Thread(target=load_model, daemon=True)
        thread.start()
    
    def select_image(self):
        """Chọn file ảnh"""
        file_path = filedialog.askopenfilename(
            title="Chọn ảnh",
            filetypes=[
                ("Ảnh", "*.png *.jpg *.jpeg *.bmp *.tiff"),
                ("Tất cả", "*.*")
            ]
        )
        
        if file_path:
            self.image_path = file_path
            self.file_label.config(text=os.path.basename(file_path), foreground="black")
            self.display_image_preview(file_path)
    
    def display_image_preview(self, image_path):
        """Hiển thị ảnh xem trước"""
        try:
            img = Image.open(image_path)
            
            # Resize ảnh để fit vào frame
            max_width = 400
            max_height = 300
            
            img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            
            self.display_image = ImageTk.PhotoImage(img)
            self.image_label.config(image=self.display_image, text="")
        except Exception as e:
            self.image_label.config(image="", text=f"Lỗi hiển thị ảnh: {str(e)}")
    
    def preprocess_image_tesseract(self, image_path):
        """Tiền xử lý ảnh cho Tesseract"""
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Không thể đọc ảnh từ: {image_path}")
        
        img = cv2.resize(img, None, fx=2.5, fy=2.5, interpolation=cv2.INTER_CUBIC)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
        gray = clahe.apply(gray)
        gray = cv2.GaussianBlur(gray, (3, 3), 0)
        
        kernel_sharp = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        gray = cv2.filter2D(gray, -1, kernel_sharp)
        
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        return thresh
    
    def preprocess_image_vietocr(self, image_path):
        """Tiền xử lý ảnh cho VietOCR"""
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Không thể đọc ảnh từ: {image_path}")
        
        img = cv2.resize(img, None, fx=2.5, fy=2.5, interpolation=cv2.INTER_CUBIC)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        gray = clahe.apply(gray)
        gray = cv2.GaussianBlur(gray, (3, 3), 0)
        
        binary = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 31, 5
        )
        
        rgb = cv2.cvtColor(binary, cv2.COLOR_GRAY2RGB)
        pil_img = Image.fromarray(rgb)
        
        return pil_img
    
    def run_ocr_tesseract(self, image_path, lang):
        """Chạy OCR bằng Tesseract"""
        if not TESSERACT_AVAILABLE:
            raise Exception("Tesseract OCR chưa được cài đặt!")
        
        processed_img = self.preprocess_image_tesseract(image_path)
        custom_config = r"--oem 3 --psm 6 -c preserve_interword_spaces=1"
        
        text = pytesseract.image_to_string(
            processed_img,
            lang=lang,
            config=custom_config
        ).strip()
        
        return text
    
    def run_ocr_vietocr(self, image_path):
        """Chạy OCR bằng VietOCR"""
        if not VIETOCR_AVAILABLE:
            raise Exception("VietOCR chưa được cài đặt!")
        
        if self.vietocr_processor is None:
            raise Exception("VietOCR model chưa được tải! Vui lòng đợi...")
        
        processed_img = self.preprocess_image_vietocr(image_path)
        text = self.vietocr_processor.predict(processed_img)
        
        return text.strip()
    
    def run_ocr(self):
        """Chạy OCR (trong thread riêng để không block UI)"""
        if not self.image_path:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn ảnh trước!")
            return
        
        method = self.ocr_method.get()
        if method == "none":
            messagebox.showerror("Lỗi", "Không có phương pháp OCR nào khả dụng!")
            return
        
        def ocr_worker():
            try:
                self.status_var.set("Đang xử lý OCR...")
                self.result_text.delete(1.0, tk.END)
                self.result_text.insert(tk.END, "Đang xử lý...\n")
                self.root.update()
                
                if method == "tesseract":
                    lang = self.lang_var.get()
                    text = self.run_ocr_tesseract(self.image_path, lang)
                elif method == "vietocr":
                    text = self.run_ocr_vietocr(self.image_path)
                else:
                    text = "Phương pháp không hợp lệ!"
                
                # Cập nhật UI trong main thread
                self.root.after(0, lambda: self.display_result(text, method))
                
            except Exception as e:
                error_msg = f"Lỗi: {str(e)}"
                self.root.after(0, lambda: self.display_error(error_msg))
        
        thread = threading.Thread(target=ocr_worker, daemon=True)
        thread.start()
    
    def display_result(self, text, method):
        """Hiển thị kết quả OCR"""
        self.result_text.delete(1.0, tk.END)
        
        header = f"=== KẾT QUẢ OCR ({method.upper()}) ===\n"
        header += "=" * 50 + "\n\n"
        self.result_text.insert(tk.END, header)
        self.result_text.insert(tk.END, text)
        
        if not text:
            self.result_text.insert(tk.END, "\n⚠️ Không tìm thấy text trong ảnh")
        
        self.status_var.set(f"Hoàn thành! (Phương pháp: {method})")
    
    def display_error(self, error_msg):
        """Hiển thị lỗi"""
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, f"❌ {error_msg}")
        self.status_var.set("Có lỗi xảy ra!")
        messagebox.showerror("Lỗi", error_msg)
    
    def copy_result(self):
        """Sao chép kết quả vào clipboard"""
        text = self.result_text.get(1.0, tk.END).strip()
        if text:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            messagebox.showinfo("Thành công", "Đã sao chép kết quả vào clipboard!")
        else:
            messagebox.showwarning("Cảnh báo", "Không có kết quả để sao chép!")
    
    def save_result(self):
        """Lưu kết quả vào file"""
        text = self.result_text.get(1.0, tk.END).strip()
        if not text:
            messagebox.showwarning("Cảnh báo", "Không có kết quả để lưu!")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Lưu kết quả",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(text)
                messagebox.showinfo("Thành công", f"Đã lưu kết quả vào:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể lưu file:\n{str(e)}")


def main():
    """Hàm main để chạy ứng dụng GUI"""
    root = tk.Tk()
    app = OCRApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

