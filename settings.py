import os
import pygame

# --- 遊戲網格與尺寸設定 ---
GRID_SIZE = 50 # 每個格子的像素大小
GRID_WIDTH = 20 # 遊戲區域的格子寬度
GRID_HEIGHT = 20 # 遊戲區域的格子高度
GAME_WIDTH = GRID_WIDTH * GRID_SIZE # 遊戲區域的總像素寬度
GAME_HEIGHT = GRID_HEIGHT * GRID_SIZE # 遊戲區域的總像素高度

# --- 視窗設定 ---
BORDER_PERCENTAGE = 0.8 # 初始視窗大小佔螢幕寬/高的最大比例 (用於留邊)
MIN_WINDOW_SIZE = 400 # 視窗的最小像素尺寸

# --- 顏色定義 (RGB) ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 50, 50) # 普通蘋果顏色
GOLD = (255, 215, 0) # 金蘋果顏色
PURPLE = (128, 0, 128) # 毒藥顏色
BRIGHT_RED = (255, 0, 0) # 遊戲結束標題顏色
GREEN = (0, 200, 0) # 玩家 1 蛇身體顏色
DARK_GREEN = (0, 150, 0) # 玩家 1 蛇頭顏色/漸變目標色
BLUE = (0, 150, 255) # 玩家 2 / AI 蛇身體顏色
DARK_BLUE = (0, 100, 200) # 玩家 2 / AI 蛇頭顏色/漸變目標色
BRIGHT_GREEN = (50, 255, 50) # 可能用於高亮或其他效果 (目前未使用)
CHECKERBOARD_COLOR_1 = (20, 20, 30) # 棋盤格背景顏色 1 (深)
CHECKERBOARD_COLOR_2 = (25, 25, 35) # 棋盤格背景顏色 2 (稍淺)
OVERLAY_COLOR = (0, 0, 20, 180) # 遊戲結束/暫停時的疊加層顏色 (深藍半透明)
BUTTON_COLOR = (0, 100, 50) # 按鈕正常顏色
BUTTON_HOVER_COLOR = (0, 150, 80) # 按鈕懸停顏色
TEXT_COLOR = WHITE # 大部分文字顏色
TITLE_COLOR = (220, 220, 255) # 主選單標題和暫停標題顏色 (淡藍紫)
HIGHLIGHT_COLOR = (255, 255, 100) # 暫停提示文字顏色 (淡黃色)

# --- 檔案路徑設定 ---
GAME_DIR = os.path.dirname(os.path.abspath(__file__)) # 獲取當前檔案所在目錄
ASSETS_DIR = os.path.join(GAME_DIR, "assets") # 資源總目錄
FONTS_DIR = os.path.join(ASSETS_DIR, "fonts") # 字體目錄
IMAGES_DIR = os.path.join(ASSETS_DIR, "images") # 圖片總目錄
FOOD_IMAGE_DIR = os.path.join(IMAGES_DIR, "food") # 食物圖片目錄
SOUNDS_DIR = os.path.join(ASSETS_DIR, "sounds") # 音效目錄

# --- 字體設定 ---
FONT_NAME = "Cubic_11.ttf" # 字體檔案名稱
FONT_PATH = os.path.join(FONTS_DIR, FONT_NAME) # 完整字體檔案路徑
SCORE_FONT_SIZE = 36 # 分數文字大小
GAME_OVER_FONT_SIZE = 72 # 遊戲結束標題文字大小
MENU_TITLE_FONT_SIZE = 80 # 主選單標題文字大小
MENU_BUTTON_FONT_SIZE = 45 # 主選單按鈕文字大小

# --- 食物設定 ---
# 預設食物圖片路徑 (如果特定類型未指定)
FOOD_IMAGE_PATH = os.path.join(FOOD_IMAGE_DIR, "Apple.png")
GOLDEN_APPLE_IMAGE_PATH = os.path.join(FOOD_IMAGE_DIR, "GoldenApple.png")
POISON_IMAGE_PATH = os.path.join(FOOD_IMAGE_DIR, "Poison.png")
# 定義不同食物類型的屬性
FOOD_TYPES = [
    {'type': 'apple', 'score': 1, 'probability': 0.90, 'image': FOOD_IMAGE_PATH, 'color': RED}, # 普通蘋果
    {'type': 'golden_apple', 'score': 5, 'probability': 0.03, 'image': GOLDEN_APPLE_IMAGE_PATH, 'color': GOLD}, # 金蘋果
    {'type': 'poison', 'score': -3, 'probability': 0.07, 'image': POISON_IMAGE_PATH, 'color': PURPLE} # 毒藥
]
# 提取各食物類型的生成概率，用於 random.choices
FOOD_PROBABILITIES = [item['probability'] for item in FOOD_TYPES]
FOOD_TIMEOUT = 10000 # 食物存在時間 (毫秒)，超時會消失
MAX_FOOD_SINGLE = 2 # 單人模式下畫面上的最大食物數量
MAX_FOOD_MULTI = 5 # 多人/AI 模式下畫面上的最大食物數量

# --- 音效路徑設定 ---
EATING_SOUND_PATH = os.path.join(SOUNDS_DIR, "eating.mp3") # 吃食物音效
GAMEOVER_SOUND_PATH = os.path.join(SOUNDS_DIR, "gameover.mp3") # 遊戲結束音效
SELECT_SOUND_PATH = os.path.join(SOUNDS_DIR, "select.mp3") # 選單選擇音效

# --- 遊戲機制設定 ---
SNAKE_SPEED = 10 # 遊戲速度 (幀率，數值越高蛇移動越快)

# --- 玩家控制設定 ---
# 玩家 1 的按鍵映射 (方向鍵)
PLAYER1_CONTROLS = {
    pygame.K_UP: (0, -1), # 上
    pygame.K_DOWN: (0, 1), # 下
    pygame.K_LEFT: (-1, 0), # 左
    pygame.K_RIGHT: (1, 0) # 右
}
# 玩家 2 的按鍵映射 (WASD)
PLAYER2_CONTROLS = {
    pygame.K_w: (0, -1), # 上 (W)
    pygame.K_s: (0, 1), # 下 (S)
    pygame.K_a: (-1, 0), # 左 (A)
    pygame.K_d: (1, 0) # 右 (D)
} 