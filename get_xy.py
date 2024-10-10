# get_xy.py
import pyautogui
import tkinter as tk

def show_mouse_position():
    root = tk.Tk()
    root.title("鼠标位置监视")
    root.geometry("300x100")

    position_label = tk.Label(root, text="鼠标位置: x=0, y=0", font=("Arial", 16))
    position_label.pack(pady=20)

    def update_position():
        x, y = pyautogui.position()
        position_label.config(text=f"鼠标位置: x={x}, y={y}")
        root.after(100, update_position)

    update_position()
    root.mainloop()
