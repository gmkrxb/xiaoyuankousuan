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

# 配置 tesseract 的可执行文件路径
pytesseract.pytesseract.tesseract_cmd = r'/opt/homebrew/bin/tesseract'

# 初始化全局变量

# 坐标的格式(x1,y1,x3,y3)=>(左上角x坐标，左上角y坐标，右下角x坐标，右下角y坐标)
# 数字区域的坐标
number_region = (170, 250, 510, 370)
# 绘图区域的坐标
draw_region = (176, 522, 472, 813)

# 分割图像偏移单位，左边图像
x_l_mo = 45
# 分割图像偏移单位，右边图像
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

# 开始识别与作答的函数
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

# 作答任务线程
def task_thread(total_questions, answer_interval, prepare_time):
    log_text.insert(tk.END, f"准备开始，等待 {prepare_time} 秒...\n")
    time.sleep(prepare_time)

    custom_oem_psm_config = r'--oem 3 --psm 6'

    for i in range(total_questions):
        log_text.insert(tk.END, f"开始第 {i + 1} 题...\n")
        # 进行数字区域的截图并识别
        screenshot = ImageGrab.grab(bbox=number_region)
        if screenshot.width == 0 or screenshot.height == 0:
            log_text.insert(tk.END, f"第 {i + 1} 题：区域截图失败，宽度或高度为 0\n")
            continue

        # 显示原始截图在GUI窗口中
        screenshot_tk = ImageTk.PhotoImage(screenshot)
        screenshot_label.config(image=screenshot_tk)
        screenshot_label.image = screenshot_tk

        img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        height, width = img.shape[:2]
        mid_x = width // 2

        # 分割图像为左右两部分，并偏移以避开中间圆圈
        left_img = img[:, :mid_x - x_l_mo]
        right_img = img[:, mid_x + x_r_mo:]

        # 保存图像到 temp 文件夹
        left_img_path = f'temp/{i + 1}_l.png'
        right_img_path = f'temp/{i + 1}_r.png'
        cv2.imwrite(left_img_path, left_img, [cv2.IMWRITE_PNG_COMPRESSION, 1])  # 使用较高压缩等级加快处理速度
        cv2.imwrite(right_img_path, right_img, [cv2.IMWRITE_PNG_COMPRESSION, 1])

        # 显示左右图像在GUI窗口中
        left_processed_img = Image.fromarray(left_img)
        left_processed_img_tk = ImageTk.PhotoImage(left_processed_img)
        left_processed_label.config(image=left_processed_img_tk)
        left_processed_label.image = left_processed_img_tk

        right_processed_img = Image.fromarray(right_img)
        right_processed_img_tk = ImageTk.PhotoImage(right_processed_img)
        right_processed_label.config(image=right_processed_img_tk)
        right_processed_label.image = right_processed_img_tk

        nums = []
        for img_path, label in [(left_img_path, left_num_roi_label), (right_img_path, right_num_roi_label)]:
            # OCR识别
            result = pytesseract.image_to_string(Image.open(img_path), config=custom_oem_psm_config).strip()
            # 保留数字
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

        # 比较
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
    # 定义两条平行的短线来代表等于号
    pyautogui.moveTo(region[0] + 40, region[1] + 70)
    pyautogui.mouseDown()
    pyautogui.moveRel(40, 0, duration=0.1)
    pyautogui.mouseUp()

    pyautogui.moveTo(region[0] + 40, region[1] + 90)
    pyautogui.mouseDown()
    pyautogui.moveRel(40, 0, duration=0.1)
    pyautogui.mouseUp()


# 创建GUI窗口
root = tk.Tk()
root.title("自动比大小脚本")
root.geometry("800x1500")


# 数字区域设置
frame_top = tk.Frame(root, bg="#e0e0e0")
frame_top.pack(pady=10)
tk.Label(frame_top, text="数字区域坐标: x1, y1, x3, y3 (左上角和右下角)", bg="#e0e0e0", font=("Helvetica", 12, "bold")).pack()
region_x1_entry = tk.Entry(frame_top, width=5)
region_x1_entry.insert(0, number_region[0])
region_x1_entry.pack(side=tk.LEFT, padx=2)
region_y1_entry = tk.Entry(frame_top, width=5)
region_y1_entry.insert(0, number_region[1])
region_y1_entry.pack(side=tk.LEFT, padx=2)
region_x3_entry = tk.Entry(frame_top, width=5)
region_x3_entry.insert(0, number_region[2])
region_x3_entry.pack(side=tk.LEFT, padx=2)
region_y3_entry = tk.Entry(frame_top, width=5)
region_y3_entry.insert(0, number_region[3])
region_y3_entry.pack(side=tk.LEFT, padx=2)
number_region_btn = tk.Button(frame_top, text="设置数字区域", command=select_region, bg="#388E3C", fg="white", font=("Helvetica", 10, "bold"))
number_region_btn.pack(pady=5)

# 绘图区域设置
frame_middle = tk.Frame(root, bg="#e0e0e0")
frame_middle.pack(pady=10)
tk.Label(frame_middle, text="绘图区域坐标: x1, y1, x3, y3 (左上角和右下角)", bg="#e0e0e0", font=("Helvetica", 12, "bold")).pack()
draw_x1_entry = tk.Entry(frame_middle, width=5)
draw_x1_entry.insert(0, draw_region[0])
draw_x1_entry.pack(side=tk.LEFT, padx=2)
draw_y1_entry = tk.Entry(frame_middle, width=5)
draw_y1_entry.insert(0, draw_region[1])
draw_y1_entry.pack(side=tk.LEFT, padx=2)
draw_x3_entry = tk.Entry(frame_middle, width=5)
draw_x3_entry.insert(0, draw_region[2])
draw_x3_entry.pack(side=tk.LEFT, padx=2)
draw_y3_entry = tk.Entry(frame_middle, width=5)
draw_y3_entry.insert(0, draw_region[3])
draw_y3_entry.pack(side=tk.LEFT, padx=2)
draw_region_btn = tk.Button(frame_middle, text="设置绘图区域", command=select_draw_region, bg="#388E3C", fg="white", font=("Helvetica", 10, "bold"))
draw_region_btn.pack(pady=5)

# 设置参数
frame_params = tk.Frame(root, bg="#e0e0e0")
frame_params.pack(pady=10)
tk.Label(frame_params, text="作答题数:", bg="#e0e0e0", font=("Helvetica", 12, "bold")).pack()
question_count_entry = tk.Entry(frame_params)
question_count_entry.pack()

tk.Label(frame_params, text="作答间隔(秒):", bg="#e0e0e0", font=("Helvetica", 12, "bold")).pack()
answer_interval_entry = tk.Entry(frame_params)
answer_interval_entry.pack()

tk.Label(frame_params, text="开始前准备时间(秒):", bg="#e0e0e0", font=("Helvetica", 12, "bold")).pack()
prepare_time_entry = tk.Entry(frame_params)
prepare_time_entry.pack()

# 获取鼠标坐标
mouse_position_btn = tk.Button(root, text="获取鼠标坐标", command=show_mouse_position, fg="black", font=("Helvetica", 14, "bold"))
mouse_position_btn.pack(pady=10)

# 开始按钮
start_btn = tk.Button(root, text="开始", command=start_task, fg="black", font=("Helvetica", 14, "bold"))
start_btn.pack(pady=10)

# 日志框
log_text = tk.Text(root, height=10, font=("Helvetica", 12), bg="#ffffff", fg="#000000")
log_text.pack(pady=10)

# 显示原始截图区域
screenshot_label = tk.Label(root, bg="#e0e0e0")
screenshot_label.pack(pady=10)

# 显示处理后的左半部分图像区域
left_processed_label = tk.Label(root, bg="#e0e0e0")
left_processed_label.pack(pady=10)

# 显示处理后的右半部分图像区域
right_processed_label = tk.Label(root, bg="#e0e0e0")
right_processed_label.pack(pady=10)

# 显示待识别的左侧数字区域
left_num_roi_label = tk.Label(root, bg="#e0e0e0")
left_num_roi_label.pack(pady=10)

# 显示待识别的右侧数字区域
right_num_roi_label = tk.Label(root, bg="#e0e0e0")
right_num_roi_label.pack(pady=10)

root.mainloop()