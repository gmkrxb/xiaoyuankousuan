
# 基于OCR识别的小猿口算比大小自动做题程序（支持0~100比较）

## 开发信息
- **开发平台**: PyCharm
- **编译器版本**: Python 3.12
- **开发系统**: macOS 15

## 功能介绍
该程序通过 OCR 技术对小猿口算中的0-100数字进行自动识别，并在屏幕上进行比大小操作。支持自动抓取屏幕上的数字，并在识别后比较，在绘制区域自动绘制符号（`>`, `<`, `=`）。


## 联系信息
- **开发人员**: Mark Gu
- **官网**: [https://gumingke.cloud](https://gumingke.cloud)
- **邮箱**: [gumingke@gmk.cloud](mailto:gumingke@gmk.cloudgumingke@gmk.cloud)

## 项目结构
```
.
├── README.md                             # 使用说明文档
├── comparison.py                         # 对比 easyocr 和 tesseract 的识别时间和结果
├── get_xy.py                             # 获取鼠标坐标的库
├── main.py                               # 主程序
├── temp                                  # 文件夹，用于保存分割之后的图片
│   └── ...                               # 分割保存的图片
└── test_photo.png                        # 测试 comparison.py 的图片
```

## 使用方法

### 环境依赖
在运行本程序前，需要安装以下 Python 库：

1. 使用官方源安装：
   ```bash
   pip install pyautogui opencv-python pillow pytesseract numpy
   ```
2. 使用清华源安装：
   ```bash
   pip install -i https://pypi.tuna.tsinghua.edu.cn/simple pyautogui opencv-python pillow pytesseract numpy
   ```

### Tesseract 配置
OCR 依赖 Tesseract，请按照以下步骤在 Windows 或 macOS 上进行配置：

#### 在 Windows 上安装 Tesseract
1. **文件下载**:
   - 下载地址: [Tesseract 官方下载](https://github.com/UB-Mannheim/tesseract/wiki)
   - 下载并安装，安装路径如 `C:\Program Files\Tesseract-OCR`。
   - 配置环境变量:
     - 将 Tesseract 安装路径添加到系统环境变量 `PATH` 中（如何添加：[点我查看](https://jingyan.baidu.com/article/49711c61197cadba451b7c6f.html))）。

2.**配置 Tesseract 的可执行文件路径**:
   - 打开安装目录（例如 `C:\Program Files\Tesseract-OCR`），找到 `tesseract.exe`。
   - 在代码中设置 Tesseract 路径：
     ```python
     pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
     ```

#### 在 macOS 上安装 Tesseract
1. **安装 Homebrew**:
   - 如果你的系统还未安装 Homebrew，可以通过以下命令安装 Homebrew:
     ```bash
     /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
     ```
   - 安装完成后，按终端提示运行配置命令，使 Homebrew 生效。

2. **使用 Homebrew 安装 Tesseract**:
   - 官方源安装:
     ```bash
     brew install tesseract
     ```
   - 或者使用清华源（国内用户）:
     - 替换 Homebrew 镜像源为清华源（如果未配置过）:
       ```bash
       git -C "$(brew --repo)" remote set-url origin https://mirrors.tuna.tsinghua.edu.cn/homebrew/brew.git
       git -C "$(brew --repo homebrew/core)" remote set-url origin https://mirrors.tuna.tsinghua.edu.cn/homebrew/homebrew-core.git
       ```
     - 然后安装 Tesseract:
       ```bash
       brew install tesseract
       ```

3. **配置 Tesseract 的可执行文件路径**:
   - 获取 Tesseract 的可执行文件路径:
     ```bash
     which tesseract
     ```
     该命令将输出类似 `/opt/homebrew/bin/tesseract` 的路径。
   - 在代码中设置 Tesseract 路径：
     ```python
     pytesseract.pytesseract.tesseract_cmd = r'/opt/homebrew/bin/tesseract'
     ```

#### 验证 Tesseract 安装
在**终端**(macOS)或**命令行**(Windows)中输入以下命令，验证是否正确安装:
```bash
tesseract -v
```
如果成功显示版本信息，则安装成功。

### 使用流程
1. **运行主程序**:
   在命令行中运行 `main.py`:
   ```bash
   python main.py
   ```
2. **获取鼠标坐标**:
   - 点击程序中的“获取鼠标坐标”按钮。
   - 根据提示，将需要的坐标值填写在 `number_region` 和 `draw_region` 中。

3. **调整全局变量**:
   在 `main.py` 中，根据实际需要调整以下全局变量：
    
   | 变量名称         | 含义                | 示例值                  |
   |------------------|-------------------|-------------------------|
   | `number_region`  | 数字区域的坐标，用于识别数字的位置 | `(170, 250, 510, 370)`  |
   | `draw_region`    | 绘图区域的坐标，用于绘制符号的位置 | `(176, 522, 472, 813)`  |
   | `x_l_mo`         | 左边图像的分割偏移量        | `45`                    |
   | `x_r_mo`         | 右边图像的分割偏移量        | `40`                    |
    **注意**：坐标的格式 `(x1,y1,x3,y3)` => `(左上角x坐标，左上角y坐标，右下角x坐标，右下角y坐标)`

4. **设置作答参数**:
   - 输入“作答题数”、“作答间隔（秒）”和“准备时间（秒）”。
   - 建议“作答题数”比实际题数多 3~5，以保证程序运行过程中有足够的时间和题数。

5. **开始运行**:
   点击“开始”按钮，程序将自动识别并进行作答。

