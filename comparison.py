import cv2
import pytesseract
import time
import easyocr

# 配置tesseract的可执行文件路径
pytesseract.pytesseract.tesseract_cmd = r'/opt/homebrew/bin/tesseract'

# 加载图像
image_path = 'test_photo.png'
image = cv2.imread(image_path)

# 转换为灰度图像
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# 对比easyocr和tesseract的识别时间和结果

# 使用Tesseract进行OCR识别
start_time_tesseract = time.time()
custom_oem_psm_config = r'--oem 3 --psm 6'
text_tesseract = pytesseract.image_to_string(gray, config=custom_oem_psm_config)
end_time_tesseract = time.time()

# 使用easyocr进行OCR识别
reader = easyocr.Reader(['ch_sim', 'en'])
start_time_easyocr = time.time()
result_easyocr = reader.readtext(image_path)
end_time_easyocr = time.time()

# 输出Tesseract的识别结果和时间
print("Tesseract识别结果:")
print(text_tesseract)
print(f"Tesseract识别时间: {end_time_tesseract - start_time_tesseract:.2f}秒")

# 输出easyocr的识别结果和时间
print("\nEasyOCR识别结果:")
for res in result_easyocr:
    print(res)
print(f"EasyOCR识别时间: {end_time_easyocr - start_time_easyocr:.2f}秒")