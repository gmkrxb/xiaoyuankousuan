import tkinter as tk
from tkinter import messagebox, PhotoImage
import pyautogui
import cv2
import numpy as np
import time
import threading
from PIL import ImageGrab, Image, ImageTk
import pytesseract
import os
from get_xy import show_mouse_position

# 默认填充图像
default_image_path = "bg.png"

# 配置 tesseract 的可执行文件路径
pytesseract.pytesseract.tesseract_cmd = r'/opt/homebrew/bin/tesseract'

# 初始化全局变量
number_region = (170, 250, 510, 370)
draw_region = (176, 522, 472, 813)

x_l_mo = 45
x_r_mo = 40

# 创建 temp 文件夹存储处理后的图像
os.makedirs('temp', exist_ok=True)


# 选择数字区域的函数
def select_region():
    global number_region
    try:
        x1 = int(region_x1_entry.get())
        y1 = int(region_y1_entry.get())
        x3 = int(region_x3_entry.get())
        y3 = int(region_y3_entry.get())
        left = min(x1, x3)
        top = min(y1, y3)
        right = max(x1, x3)
        bottom = max(y1, y3)
        number_region = (left, top, right, bottom)
        messagebox.showinfo("提示", f"数字区域已设置: {number_region}")
    except ValueError:
        messagebox.showerror("错误", "请输入有效的坐标值！")


# 选择绘图区域的函数
def select_draw_region():
    global draw_region
    try:
        x1 = int(draw_x1_entry.get())
        y1 = int(draw_y1_entry.get())
        x3 = int(draw_x3_entry.get())
        y3 = int(draw_y3_entry.get())
        left = min(x1, x3)
        top = min(y1, y3)
        right = max(x1, x3)
        bottom = max(y1, y3)
        draw_region = (left, top, right, bottom)
        messagebox.showinfo("提示", f"绘图区域已设置: {draw_region}")
    except ValueError:
        messagebox.showerror("错误", "请输入有效的坐标值！")


# 开始任务的函数
def start_task():
    if not number_region or not draw_region:
        messagebox.showwarning("警告", "请先设置数字区域和绘图区域！")
        return

    try:
        total_questions = int(question_count_entry.get())
        answer_interval = float(answer_interval_entry.get())
        prepare_time = int(prepare_time_entry.get())
    except ValueError:
        messagebox.showerror("错误", "请输入有效的数字设置！")
        return

    # 启动线程，阻止阻塞主界面
    threading.Thread(target=task_thread, args=(total_questions, answer_interval, prepare_time)).start()


# 作答任务的线程函数
def task_thread(total_questions, answer_interval, prepare_time):
    log_text.insert(tk.END, f"准备开始，等待 {prepare_time} 秒...\n")
    time.sleep(prepare_time)

    custom_oem_psm_config = r'--oem 3 --psm 6'

    for i in range(total_questions):
        log_text.insert(tk.END, f"开始第 {i + 1} 题...\n")
        # 进行数字区域的截图
        screenshot = ImageGrab.grab(bbox=number_region)
        if screenshot.width == 0 or screenshot.height == 0:
            log_text.insert(tk.END, f"第 {i + 1} 题：区域截图失败，宽度或高度为 0\n")
            continue

        # 显示原始截图在 GUI 窗口中
        screenshot_tk = ImageTk.PhotoImage(screenshot)
        screenshot_label.config(image=screenshot_tk)
        screenshot_label.image = screenshot_tk

        # 转换截图为 OpenCV 图像格式
        img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        height, width = img.shape[:2]
        mid_x = width // 2

        # 分割图像为左右两部分
        left_img = img[:, :mid_x - x_l_mo]
        right_img = img[:, mid_x + x_r_mo:]

        # 保存图像到 temp 文件夹
        left_img_path = f'temp/{i + 1}_l.png'
        right_img_path = f'temp/{i + 1}_r.png'
        cv2.imwrite(left_img_path, left_img, [cv2.IMWRITE_PNG_COMPRESSION, 1])
        cv2.imwrite(right_img_path, right_img, [cv2.IMWRITE_PNG_COMPRESSION, 1])

        # 显示左右图像在 GUI 窗口中
        if left_img.size > 0:
            left_processed_img = Image.fromarray(left_img)
        else:
            left_processed_img = create_empty_image()
        left_processed_img_tk = ImageTk.PhotoImage(left_processed_img)
        left_processed_label.config(image=left_processed_img_tk)
        left_processed_label.image = left_processed_img_tk

        if right_img.size > 0:
            right_processed_img = Image.fromarray(right_img)
        else:
            right_processed_img = create_empty_image()
        right_processed_img_tk = ImageTk.PhotoImage(right_processed_img)
        right_processed_label.config(image=right_processed_img_tk)
        right_processed_label.image = right_processed_img_tk

        # 使用 OCR 识别左右图像中的数字
        nums = []
        for img_path in [left_img_path, right_img_path]:
            result = pytesseract.image_to_string(Image.open(img_path), config=custom_oem_psm_config).strip()
            result = ''.join(filter(str.isdigit, result))
            if result:
                try:
                    num = int(result)
                    nums.append(num)
                except ValueError:
                    log_text.insert(tk.END, f"第 {i + 1} 题：无法识别有效数字，OCR 输出：'{result}'\n")
                    nums.append(None)
            else:
                log_text.insert(tk.END, f"第 {i + 1} 题：未找到有效的数字\n")
                nums.append(None)

        # 比较识别到的数字并绘制相应的符号
        if None not in nums and len(nums) == 2:
            if nums[0] > nums[1]:
                symbol = '>'
                draw_greater_than_symbol(draw_region)
            elif nums[0] < nums[1]:
                symbol = '<'
                draw_less_than_symbol(draw_region)
            else:
                symbol = '='
                draw_equal_symbol(draw_region)

            log_text.insert(tk.END, f"第 {i + 1} 题结果：{nums[0]} {symbol} {nums[1]}\n")
        else:
            log_text.insert(tk.END, f"第 {i + 1} 题：无法识别足够的数字\n")

        time.sleep(answer_interval)


# 绘制大于符号的函数
def draw_greater_than_symbol(region):
    pyautogui.moveTo(region[0] + 60, region[1] + 60)
    pyautogui.mouseDown()
    pyautogui.moveRel(10, 10, duration=0.05)
    pyautogui.mouseDown()
    pyautogui.moveRel(-10, 1, duration=0.05)
    pyautogui.mouseUp()


# 绘制小于符号的函数
def draw_less_than_symbol(region):
    pyautogui.moveTo(region[0] + 60, region[1] + 60)
    pyautogui.mouseDown()
    pyautogui.moveRel(-10, 1, duration=0.05)
    pyautogui.mouseDown()
    pyautogui.moveRel(10, 10, duration=0.05)
    pyautogui.mouseUp()


# 绘制等于符号的函数
def draw_equal_symbol(region):
    pyautogui.moveTo(region[0] + 40, region[1] + 70)
    pyautogui.mouseDown()
    pyautogui.moveRel(40, 0, duration=0.1)
    pyautogui.mouseUp()

    pyautogui.moveTo(region[0] + 40, region[1] + 90)
    pyautogui.mouseDown()
    pyautogui.moveRel(40, 0, duration=0.1)
    pyautogui.mouseUp()


# 创建 GUI 窗口
root = tk.Tk()
root.title("自动比大小脚本")
root.geometry("750x650")
default_image = Image.open(default_image_path)

# 340x120 裁切区域
cropped_image_340x120 = default_image.crop((0, 0, 340, 120))
default_image_340x120 = ImageTk.PhotoImage(cropped_image_340x120)

# 120x120 裁切区域
cropped_image_120x120 = default_image.crop((0, 0, 120, 120))
default_image_120x120 = ImageTk.PhotoImage(cropped_image_120x120)

# 创建顶部框架用于设置数字区域
frame_top = tk.Frame(root)
frame_top.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

# 创建中间框架用于设置绘图区域
frame_middle = tk.Frame(root)
frame_middle.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

# 创建参数设置框架
frame_params = tk.Frame(root)
frame_params.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)

# 创建按钮框架
frame_buttons = tk.Frame(root)
frame_buttons.grid(row=3, column=0, sticky="nsew", padx=10, pady=10)

# 创建日志框架
frame_log = tk.Frame(root)
frame_log.grid(row=4, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)

# 创建图像显示框架
frame_images = tk.Frame(root)
frame_images.grid(row=0, column=1, rowspan=4, sticky="nsew", padx=10, pady=10)

# 数字区域设置
tk.Label(frame_top, text="数字区域坐标: x1, y1, x3, y3", font=("Helvetica", 12, "bold")).grid(row=0, column=0,
                                                                                              columnspan=4)
region_x1_entry = tk.Entry(frame_top, width=5)
region_x1_entry.insert(0, number_region[0])
region_x1_entry.grid(row=1, column=0)
region_y1_entry = tk.Entry(frame_top, width=5)
region_y1_entry.insert(0, number_region[1])
region_y1_entry.grid(row=1, column=1)
region_x3_entry = tk.Entry(frame_top, width=5)
region_x3_entry.insert(0, number_region[2])
region_x3_entry.grid(row=1, column=2)
region_y3_entry = tk.Entry(frame_top, width=5)
region_y3_entry.insert(0, number_region[3])
region_y3_entry.grid(row=1, column=3)
number_region_btn = tk.Button(frame_top, text="设置数字区域", command=select_region, font=("Helvetica", 10, "bold"))
number_region_btn.grid(row=1, column=4, padx=5)

# 绘图区域设置
tk.Label(frame_middle, text="绘图区域坐标: x1, y1, x3, y3", font=("Helvetica", 12, "bold")).grid(row=0, column=0,
                                                                                                 columnspan=4)
draw_x1_entry = tk.Entry(frame_middle, width=5)
draw_x1_entry.insert(0, draw_region[0])
draw_x1_entry.grid(row=1, column=0)
draw_y1_entry = tk.Entry(frame_middle, width=5)
draw_y1_entry.insert(0, draw_region[1])
draw_y1_entry.grid(row=1, column=1)
draw_x3_entry = tk.Entry(frame_middle, width=5)
draw_x3_entry.insert(0, draw_region[2])
draw_x3_entry.grid(row=1, column=2)
draw_y3_entry = tk.Entry(frame_middle, width=5)
draw_y3_entry.insert(0, draw_region[3])
draw_y3_entry.grid(row=1, column=3)
draw_region_btn = tk.Button(frame_middle, text="设置绘图区域", command=select_draw_region, bg="#388E3C",
                            font=("Helvetica", 10, "bold"))
draw_region_btn.grid(row=1, column=4, padx=5)

# 参数设置
tk.Label(frame_params, text="作答题数:", font=("Helvetica", 12, "bold")).grid(row=0, column=0)
question_count_entry = tk.Entry(frame_params)
question_count_entry.grid(row=0, column=1)

tk.Label(frame_params, text="作答间隔(秒):", font=("Helvetica", 12, "bold")).grid(row=1, column=0)
answer_interval_entry = tk.Entry(frame_params)
answer_interval_entry.grid(row=1, column=1)

tk.Label(frame_params, text="开始前准备时间(秒):", font=("Helvetica", 12, "bold")).grid(row=2, column=0)
prepare_time_entry = tk.Entry(frame_params)
prepare_time_entry.grid(row=2, column=1)

# 按钮
tk.Button(frame_buttons, text="获取鼠标坐标", command=show_mouse_position, fg="black", font=("Helvetica", 14, "bold"),
          bg="#008CBA").grid(row=0, column=0, padx=5, pady=5)
tk.Button(frame_buttons, text="开始", command=start_task, fg="black", font=("Helvetica", 14, "bold"),
          bg="#4CAF50").grid(row=0, column=1, padx=5, pady=5)

# 日志框
log_text = tk.Text(frame_log, height=10, font=("Helvetica", 12), bg="#ffffff", fg="#000000")
log_text.pack(fill=tk.BOTH, expand=True)

# 图像显示框架
tk.Label(frame_images, text="原始截图", font=("Helvetica", 12, "bold")).grid(row=0, column=0)
screenshot_label = tk.Label(frame_images, image=default_image_340x120)
screenshot_label.grid(row=1, column=0)
screenshot_label.image = default_image_340x120

tk.Label(frame_images, text="处理后的左半部分图像", font=("Helvetica", 12, "bold")).grid(row=2, column=0)
left_processed_label = tk.Label(frame_images, image=default_image_120x120)
left_processed_label.grid(row=3, column=0)
left_processed_label.image = default_image_120x120

tk.Label(frame_images, text="处理后的右半部分图像", font=("Helvetica", 12, "bold")).grid(row=4, column=0)
right_processed_label = tk.Label(frame_images, image=default_image_120x120)
right_processed_label.grid(row=5, column=0)
right_processed_label.image = default_image_120x120

root.mainloop()
