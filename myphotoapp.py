import cv2
import os
import numpy as np
from tkinter import filedialog
import re
from screeninfo import get_monitors

# 彈出視窗讓使用者選擇圖片資料夾
image_folder = filedialog.askdirectory(title="選擇圖片資料夾")
if not image_folder:
    print("未選擇資料夾，程式結束。")
    exit()

# 取得資料夾中的圖片檔案清單
image_files = [f for f in os.listdir(image_folder) if f.endswith(('.jpg', '.png', '.jpeg'))]
if not image_files:
    print("選擇的資料夾中沒有圖片檔案，程式結束。")
    exit()

# 檢查檔名是否包含繁體中文
def contains_traditional_chinese(text):
    traditional_chinese_pattern = re.compile(r'[\u4e00-\u9fff]')
    return bool(traditional_chinese_pattern.search(text))

for file_name in image_files:
    if contains_traditional_chinese(file_name):
        print(f"警告：檔案名稱 '{file_name}' 包含繁體中文，可能會出錯。")

# 初始化變數
current_index = 0
scale = 1.0
selection_start = None
selection_end = None
selected_region = None

# 取得螢幕解析度
monitor = get_monitors()[0]
screen_width = monitor.width
screen_height = monitor.height

def load_image(index):
    img_path = os.path.join(image_folder, image_files[index])
    print(f"正在載入圖片：{img_path}")
    img = cv2.imread(img_path)
    if img is None:
        print(f"錯誤：無法載入圖片，路徑：{img_path}")
    return img

def resize_to_fit_screen(img):
    global screen_width, screen_height
    height, width = img.shape[:2]
    if width > screen_width or height > screen_height:
        scale_factor = min(screen_width / (4 * width), screen_height / (4 * height))
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)
        img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)
    return img

def display_image(img):
    global scale
    height, width = img.shape[:2]
    resized_img = cv2.resize(img, (int(width * scale), int(height * scale)), interpolation=cv2.INTER_LINEAR)

    # 建立工具欄
    toolbar_height = 60
    toolbar = np.zeros((toolbar_height, resized_img.shape[1], 3), dtype=np.uint8)
    toolbar[:] = (200, 200, 200)

    cv2.rectangle(toolbar, (10, 10), (110, 50), (0, 255, 0), -1)
    cv2.putText(toolbar, "Next", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)

    cv2.rectangle(toolbar, (120, 10), (220, 50), (0, 255, 0), -1)
    cv2.putText(toolbar, "Prev", (130, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)

    cv2.rectangle(toolbar, (230, 10), (330, 50), (0, 255, 0), -1)
    cv2.putText(toolbar, "Reload", (240, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)

    # 合併工具欄與圖片
    combined_img = np.vstack((toolbar, resized_img))
    cv2.imshow("Image Viewer", combined_img)

def reload_images():
    global img, scale
    img = load_image(current_index)
    if img is not None:
        img = resize_to_fit_screen(img)
        display_image(img)

def show_next_image():
    global current_index, img
    current_index = (current_index + 1) % len(image_files)
    img = load_image(current_index)
    if img is not None:
        img = resize_to_fit_screen(img)
        display_image(img)

def show_previous_image():
    global current_index, img
    current_index = (current_index - 1) % len(image_files)
    img = load_image(current_index)
    if img is not None:
        img = resize_to_fit_screen(img)
        display_image(img)

def on_mouse(event, x, y, flags, param):
    global selection_start, selection_end, selected_region, img, scale, current_index
    toolbar_height = 60

    if event == cv2.EVENT_LBUTTONDOWN:
        # 點擊工具欄
        if y <= toolbar_height:
            if 10 <= x <= 110 and 10 <= y <= 50:
                show_next_image()
            elif 120 <= x <= 220 and 10 <= y <= 50:
                show_previous_image()
            elif 230 <= x <= 330 and 10 <= y <= 50:
                reload_images()
        else:
            # 記錄選取起點，還原到原始圖片座標
            selection_start = (int(x / scale), int((y - toolbar_height) / scale))

    elif event == cv2.EVENT_MOUSEMOVE and selection_start is not None:
        # 記錄選取終點，還原到原始圖片座標
        selection_end = (int(x / scale), int((y - toolbar_height) / scale))
        img_copy = img.copy()
        cv2.rectangle(img_copy, selection_start, selection_end, (0, 255, 0), 2)
        display_image(img_copy)

    elif event == cv2.EVENT_LBUTTONUP:  # 放開滑鼠左鍵
        if selection_start and selection_end:
            x1, y1 = selection_start
            x2, y2 = selection_end
            x1, x2 = sorted([x1, x2])
            y1, y2 = sorted([y1, y2])
            selected_region = img[y1:y2, x1:x2]
            if selected_region.size > 0:
                # 放大選取區域並顯示
                zoomed_region = cv2.resize(selected_region, (selected_region.shape[1] * 2, selected_region.shape[0] * 2), interpolation=cv2.INTER_LINEAR)
                cv2.imshow("Zoomed Region", zoomed_region)
            selection_start = None
            selection_end = None

    elif event == cv2.EVENT_MOUSEWHEEL:  # 滾輪縮放
        if flags > 0:
            scale += 0.1
        elif flags < 0:
            scale = max(0.1, scale - 0.1)
        display_image(img)

# 初始化 OpenCV 視窗
cv2.namedWindow("Image Viewer")
cv2.setMouseCallback("Image Viewer", on_mouse)

# 載入第一張圖片
img = load_image(current_index)
if img is not None:
    img = resize_to_fit_screen(img)
    display_image(img)

print("按 ESC 結束，方向鍵左右切換圖片，上下縮放")

# 主迴圈：持續處理鍵盤事件
while True:
    key = cv2.waitKeyEx(0)
    if key == 27:  # ESC 結束
        break
    elif key == 2424832:  # 左箭頭
        show_previous_image()
    elif key == 2555904:  # 右箭頭
        show_next_image()
    elif key == 2490368:  # 上箭頭
        scale += 0.1
        display_image(img)
    elif key == 2621440:  # 下箭頭
        scale = max(0.1, scale - 0.1)
        display_image(img)
