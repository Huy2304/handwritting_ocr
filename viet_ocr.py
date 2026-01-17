import cv2
import numpy as np
import os
from vietocr.tool.predictor import Predictor
from vietocr.tool.config import Cfg
from PIL import Image

# =========================
# CONFIG
# =========================
IMAGE_PATH = "anh/image1.png"

if not os.path.exists(IMAGE_PATH):
    raise FileNotFoundError("❌ Không tìm thấy ảnh")

# =========================
# LOAD VIETOCR MODEL
# =========================
cfg = Cfg.load_config_from_name("vgg_transformer")

cfg["device"] = "cpu"     # đổi thành "cuda" nếu có GPU
cfg["predictor"]["beamsearch"] = True
cfg["cnn"]["pretrained"] = True

vietocr = Predictor(cfg)

# =========================
# PREPROCESS IMAGE (CHUẨN CHO CHỮ NHỎ)
# =========================
img = cv2.imread(IMAGE_PATH)

# Phóng to ảnh (rất quan trọng)
img = cv2.resize(img, None, fx=2.5, fy=2.5, interpolation=cv2.INTER_CUBIC)

# Grayscale
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Tăng tương phản
clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
gray = clahe.apply(gray)

# Khử nhiễu
gray = cv2.GaussianBlur(gray, (3, 3), 0)

# Nhị phân hóa
binary = cv2.adaptiveThreshold(
    gray, 255,
    cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
    cv2.THRESH_BINARY,
    31, 5
)

# VietOCR cần ảnh RGB
rgb = cv2.cvtColor(binary, cv2.COLOR_GRAY2RGB)
pil_img = Image.fromarray(rgb)

# =========================
# OCR
# =========================
text = vietocr.predict(pil_img)

# =========================
# OUTPUT
# =========================
print("\n========== OCR RESULT ==========\n")
print(text.strip())
