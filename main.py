import pygame
import sys
import os
import math
from settings import *
from objects import Button
from game import Game

# 主遊戲類別，負責管理遊戲的整體流程、狀態和畫面顯示
class SnakeGame:
    # 初始化遊戲引擎、音效、視窗、字體和遊戲物件
    def __init__(self):
        pygame.init() # 初始化 Pygame 模組
        pygame.mixer.init() # 初始化音效模組
        self.load_sounds() # 載入遊戲音效
        self.initial_size = self.calculate_initial_window_size() # 計算初始視窗大小
        # 設定遊戲視窗，允許調整大小
        self.screen = pygame.display.set_mode(
            (self.initial_size, self.initial_size),
            pygame.RESIZABLE
        )
        pygame.display.set_caption("貪吃蛇") # 設定視窗標題
        # 載入並設定視窗圖示
        try:
            program_icon = pygame.image.load(os.path.join(ASSETS_DIR, "images", "icon.png")) # 載入圖示檔
            pygame.display.set_icon(program_icon) # 設定圖示
        except Exception as e:
            print(f"無法載入或設定圖示: {e}") # 如果載入失敗，印出錯誤訊息
        # 創建用於繪製遊戲內容的 Surface
        self.game_surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
        self.load_fonts() # 載入遊戲字體
        # 創建 Game 類別的實例，負責處理遊戲邏輯
        self.game = Game(self.screen, self.game_surface, self.sounds)
        self.buttons = [] # 初始化按鈕列表
        self.create_menu_buttons() # 創建主選單按鈕
        self.state = "menu" # 設定初始遊戲狀態為主選單
        self.game_mode = None # 初始化遊戲模式
        self.countdown_start_time = 0 # 初始化倒數計時開始時間
        self.countdown_duration = 3000 # 設定倒數計時持續時間 (毫秒)
        self.countdown_number = 3 # 初始化倒數計時數字
        self.clock = pygame.time.Clock() # 創建時脈物件以控制幀率
        self.exit_requested = False # 標記是否請求退出遊戲
        self.exit_sound_playing = False # 標記退出音效是否正在播放

    # 載入所有遊戲所需的音效檔案
    def load_sounds(self):
        """載入音效"""
        self.sounds = {
            'eating': self._load_sound(EATING_SOUND_PATH), # 載入吃食物音效
            'gameover': self._load_sound(GAMEOVER_SOUND_PATH), # 載入遊戲結束音效
            'select': self._load_sound(SELECT_SOUND_PATH) # 載入選擇音效
        }

    # 內部輔助方法，安全地載入單個音效檔案
    def _load_sound(self, path):
        """安全載入音效檔案"""
        try:
            # 檢查檔案是否存在
            if not os.path.exists(path):
                print(f"無法找到音效檔案: {path}")
                return None
            # 載入音效
            sound = pygame.mixer.Sound(path)
            return sound
        except Exception as e:
            # 處理載入錯誤
            print(f"載入音效時發生錯誤: {e}")
            return None

    # 計算初始視窗大小，使其適應螢幕尺寸並保留邊界
    def calculate_initial_window_size(self):
        """計算初始視窗大小，確保四周留有 10% 的邊界"""
        try:
            info = pygame.display.Info() # 獲取螢幕資訊
            screen_width = info.current_w # 螢幕寬度
            screen_height = info.current_h # 螢幕高度
            # 計算允許的最大寬度和高度 (保留邊界)
            max_allowable_w = int(screen_width * BORDER_PERCENTAGE)
            max_allowable_h = int(screen_height * BORDER_PERCENTAGE)
            # 取寬高中較小者作為正方形邊長
            initial_size = min(max_allowable_w, max_allowable_h)
            # 確保視窗大小不小於最小值
            initial_size = max(initial_size, MIN_WINDOW_SIZE)
            return initial_size
        except Exception:
            # 若無法獲取螢幕資訊，使用預設大小
            return 600

    # 載入遊戲所需的字體檔案，若自訂字體失敗則嘗試使用系統字體或預設字體
    def load_fonts(self):
        """載入字體"""
        try:
            # 檢查自訂字體檔案是否存在
            if not os.path.exists(FONT_PATH):
                raise FileNotFoundError(f"找不到字體檔案: {FONT_PATH}")
            # 載入標題、按鈕和倒數計時的字體
            self.title_font = pygame.font.Font(FONT_PATH, MENU_TITLE_FONT_SIZE)
            self.button_font = pygame.font.Font(FONT_PATH, MENU_BUTTON_FONT_SIZE)
            self.countdown_font = pygame.font.Font(FONT_PATH, 150)
        except Exception as e:
            # 處理自訂字體載入錯誤
            print(f"無法載入自訂字體: {e}")
            try:
                # 嘗試獲取系統可用字體
                available_fonts = pygame.font.get_fonts()
                if available_fonts:
                    # 使用第一個可用的系統字體
                    system_font = available_fonts[0]
                    self.title_font = pygame.font.SysFont(system_font, MENU_TITLE_FONT_SIZE)
                    self.button_font = pygame.font.SysFont(system_font, MENU_BUTTON_FONT_SIZE)
                    self.countdown_font = pygame.font.SysFont(system_font, 150)
                else:
                    # 若無系統字體，使用 Pygame 預設字體
                    self.title_font = pygame.font.Font(None, MENU_TITLE_FONT_SIZE)
                    self.button_font = pygame.font.Font(None, MENU_BUTTON_FONT_SIZE)
                    self.countdown_font = pygame.font.Font(None, 150)
            except Exception:
                # 若系統字體也失敗，使用 Pygame 預設字體
                self.title_font = pygame.font.Font(None, MENU_TITLE_FONT_SIZE)
                self.button_font = pygame.font.Font(None, MENU_BUTTON_FONT_SIZE)
                self.countdown_font = pygame.font.Font(None, 150)

    # 創建主選單上的按鈕 (單人、雙人、電腦、離開)
    def create_menu_buttons(self):
        """創建主畫面按鈕，包含模式選擇"""
        button_width = 350 # 按鈕寬度
        button_height = 70 # 按鈕高度
        button_spacing = 20 # 按鈕間距
        # 計算按鈕群組的總高度
        total_button_height = (button_height + button_spacing) * 4 - button_spacing
        # 計算第一個按鈕的起始 Y 座標，使其大致居中偏上
        button_y_start = GAME_HEIGHT // 2 - total_button_height // 2 + 50
        # 計算按鈕的 X 座標，使其水平居中
        button_x = GAME_WIDTH // 2 - button_width // 2
        # 創建單人遊戲按鈕
        single_button = Button(
            button_x,
            button_y_start,
            button_width,
            button_height,
            "單人遊戲",
            self.button_font
        )
        # 創建雙人對戰按鈕
        multi_button = Button(
            button_x,
            button_y_start + button_height + button_spacing,
            button_width,
            button_height,
            "雙人對戰",
            self.button_font
        )
        # 創建電腦對戰按鈕
        ai_button = Button(
            button_x,
            button_y_start + (button_height + button_spacing) * 2,
            button_width,
            button_height,
            "電腦對戰",
            self.button_font
        )
        # 創建離開遊戲按鈕
        exit_button = Button(
            button_x,
            button_y_start + (button_height + button_spacing) * 3,
            button_width,
            button_height,
            "離開遊戲",
            self.button_font
        )
        # 將所有按鈕添加到列表中
        self.buttons = [single_button, multi_button, ai_button, exit_button]

    # 處理遊戲中的所有事件，如關閉視窗、調整大小、按鍵和滑鼠點擊
    def handle_events(self):
        """處理遊戲事件"""
        events = pygame.event.get() # 獲取當前所有事件
        for event in events:
            # 處理關閉視窗事件
            if event.type == pygame.QUIT:
                # 避免重複觸發退出
                if not self.exit_sound_playing:
                    self._stop_game_sounds() # 停止遊戲結束音效
                    self._play_sound('select') # 播放選擇音效
                    self.exit_requested = True # 標記請求退出
                    self.exit_sound_playing = True # 標記音效正在播放
            # 處理視窗大小調整事件
            elif event.type == pygame.VIDEORESIZE:
                # 更新 screen 物件以反映新的視窗大小
                self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

        # 根據當前遊戲狀態分發事件處理
        if self.state == "menu":
            self.handle_menu_events(events) # 處理主選單事件
        elif self.state == "countdown":
            pass # 倒數計時狀態下不處理輸入
        elif self.state == "game":
            self.game.handle_events(events) # 將事件傳遞給 Game 物件處理遊戲內事件
            # 如果遊戲結束 (game_active 為 False)
            if not self.game.game_active:
                # 檢查是否有按鍵按下，若有則返回主選單
                for event in events:
                    if event.type == pygame.KEYDOWN:
                        self.state = "menu" # 切換回主選單狀態
                        self.game_mode = None # 重置遊戲模式
                        self._stop_game_sounds() # 停止遊戲結束音效
                        break # 找到按鍵事件後跳出迴圈

        # 處理退出請求，確保音效播放完畢後才真正退出
        if self.exit_requested and self.exit_sound_playing:
            # 檢查選擇音效是否已播放完畢
            if self.sounds['select'] and not pygame.mixer.get_busy():
                self.exit_sound_playing = False # 重置音效播放標記
                self.quit_game() # 執行退出遊戲的清理工作

    # 停止遊戲相關的音效，主要是遊戲結束音效
    def _stop_game_sounds(self):
        """停止所有遊戲音效"""
        if 'gameover' in self.sounds and self.sounds['gameover']:
            self.sounds['gameover'].stop()

    # 處理主選單狀態下的事件，主要是按鈕的點擊檢測
    def handle_menu_events(self, events):
        """處理主畫面事件"""
        mouse_pos = pygame.mouse.get_pos() # 獲取滑鼠在視窗上的座標
        # 將滑鼠螢幕座標轉換為遊戲 Surface 上的座標
        scaled_mouse_pos = self.screen_to_game_coords(mouse_pos)

        # 更新每個按鈕的懸停狀態
        for button in self.buttons:
            button.update(scaled_mouse_pos)

        mouse_clicked = False # 標記滑鼠左鍵是否在本輪事件中被點擊
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: # 1 代表滑鼠左鍵
                mouse_clicked = True

        # 如果滑鼠被點擊，檢查哪個按鈕被點擊
        if mouse_clicked:
            if self.buttons[0].check_click(scaled_mouse_pos, mouse_clicked): # 單人遊戲
                self.start_game("single")
            elif self.buttons[1].check_click(scaled_mouse_pos, mouse_clicked): # 雙人對戰
                self.start_game("multi")
            elif self.buttons[2].check_click(scaled_mouse_pos, mouse_clicked): # 電腦對戰
                self.start_game("ai")
            elif self.buttons[3].check_click(scaled_mouse_pos, mouse_clicked): # 離開遊戲
                # 避免重複觸發退出
                if not self.exit_sound_playing:
                    self._stop_game_sounds()
                    self._play_sound('select')
                    self.exit_requested = True
                    self.exit_sound_playing = True

    # 根據選擇的模式開始遊戲，進入倒數計時狀態
    def start_game(self, mode):
        """準備開始遊戲，進入倒數狀態"""
        self._play_sound('select') # 播放選擇音效
        self.game_mode = mode # 設定遊戲模式
        self.game.reset_game(mode=self.game_mode) # 重置 Game 物件的狀態
        self.state = "countdown" # 切換到倒數計時狀態
        self.countdown_start_time = pygame.time.get_ticks() # 記錄倒數開始時間
        self.countdown_number = 3 # 重置倒數數字

    # 播放指定名稱的音效
    def _play_sound(self, sound_name):
        """播放指定音效"""
        sound = self.sounds.get(sound_name) # 從字典中獲取音效物件
        if sound:
            sound.play() # 播放音效

    # 將螢幕上的座標轉換為固定大小的遊戲 Surface 上的座標
    def screen_to_game_coords(self, screen_pos):
        """將螢幕座標轉換為遊戲座標"""
        window_width, window_height = self.screen.get_size() # 獲取當前視窗大小
        aspect_ratio = GAME_WIDTH / GAME_HEIGHT # 計算遊戲內容的寬高比
        # 根據視窗寬高比和遊戲內容寬高比，計算縮放比例和偏移量
        if window_width / window_height >= aspect_ratio:
            # 視窗較寬，以高度為基準縮放
            scale_h = window_height
            scale_w = int(scale_h * aspect_ratio)
            scaled_rect_x = (window_width - scale_w) // 2 # 計算左右黑邊寬度
            scaled_rect_y = 0
        else:
            # 視窗較高，以寬度為基準縮放
            scale_w = window_width
            scale_h = int(scale_w / aspect_ratio)
            scaled_rect_x = 0
            scaled_rect_y = (window_height - scale_h) // 2 # 計算上下黑邊高度
        # 根據縮放比例和偏移量，反算出在遊戲 Surface 上的座標
        x = (screen_pos[0] - scaled_rect_x) * GAME_WIDTH / scale_w
        y = (screen_pos[1] - scaled_rect_y) * GAME_HEIGHT / scale_h
        return (x, y)

    # 繪製主選單畫面
    def draw_menu(self):
        """繪製主畫面，增強標題效果和整體視覺體驗"""
        self.game.draw_background() # 繪製棋盤格背景
        # 繪製半透明疊加層，使背景變暗，突出前景元素
        overlay = pygame.Surface((GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA) # SRCALPHA 支持透明度
        overlay.fill((0, 0, 20, 50)) # 深藍色，低透明度
        self.game_surface.blit(overlay, (0, 0))
        self.draw_decorative_snake() # 繪製裝飾性的蛇圖案

        # 繪製遊戲標題文字
        title_text = "貪吃蛇"
        shadow_offset = 4 # 陰影偏移量
        shadow_color = (0, 0, 0, 180) # 黑色半透明陰影
        # 渲染標題陰影
        shadow_surface = self.title_font.render(title_text, False, shadow_color)
        shadow_rect = shadow_surface.get_rect(
            center=(GAME_WIDTH // 2 + shadow_offset, GAME_HEIGHT // 3 + shadow_offset) # 中心對齊並偏移
        )
        self.game_surface.blit(shadow_surface, shadow_rect)
        # 渲染標題文字本身
        title_surface = self.title_font.render(title_text, False, TITLE_COLOR)
        title_rect = title_surface.get_rect(center=(GAME_WIDTH // 2, GAME_HEIGHT // 3)) # 中心對齊
        self.game_surface.blit(title_surface, title_rect)

        # 添加標題高光效果，使其閃爍
        current_time = pygame.time.get_ticks() # 獲取當前時間
        # 使用正弦函數計算閃爍強度
        highlight_intensity = int(40 * abs(math.sin(current_time * 0.002)) + 20)
        # 計算高光顏色
        highlight_color = (
            min(255, TITLE_COLOR[0] + highlight_intensity), # 增加 R
            min(255, TITLE_COLOR[1] + highlight_intensity), # 增加 G
            min(255, TITLE_COLOR[2]) # B 不變
        )
        # 渲染高光文字
        highlight_surface = self.title_font.render(title_text, False, highlight_color)
        # 在原標題位置繪製高光文字，覆蓋部分原文字產生效果
        self.game_surface.blit(highlight_surface, title_rect)

        # 繪製所有按鈕
        for button in self.buttons:
            button.draw(self.game_surface)

    # 在主選單繪製一個裝飾性的靜態蛇圖案
    def draw_decorative_snake(self):
        """繪製裝飾性蛇圖案，移到右上角位置避開標題"""
        # 定義蛇身體的格子座標
        segments = [
            (15, 4), (14, 4), (13, 4), (12, 4), (11, 4), (10, 4), (9, 4),
            (9, 5), (9, 6), (10, 6), (11, 6), (12, 6), (13, 6), (13, 7),
            (13, 8), (12, 8), (11, 8), (10, 8), (9, 8), (9, 9)
        ]
        # 遍歷每個身體部分進行繪製
        for i, segment in enumerate(segments):
            segment_length = len(segments)
            # 計算漸變強度，使蛇頭到蛇尾顏色漸變
            gradient_intensity = min(1.0, i / (segment_length - 1) * 1.2)
            # 根據漸變強度計算當前身體部分的顏色 (從 DARK_GREEN 到 GREEN)
            r = int(DARK_GREEN[0] + (GREEN[0] - DARK_GREEN[0]) * gradient_intensity)
            g = int(DARK_GREEN[1] + (GREEN[1] - DARK_GREEN[1]) * gradient_intensity)
            b = int(DARK_GREEN[2] + (GREEN[2] - DARK_GREEN[2]) * gradient_intensity)
            segment_color = (r, g, b)
            # 計算身體部分的矩形區域
            rect = pygame.Rect(
                int(segment[0] * GRID_SIZE), # 格子 X 座標 * 格子大小
                int(segment[1] * GRID_SIZE), # 格子 Y 座標 * 格子大小
                GRID_SIZE, GRID_SIZE
            )
            # 計算內部矩形，用於繪製帶邊框效果的圓角矩形
            inner_rect = pygame.Rect(
                rect.x + 1, rect.y + 1,
                rect.width - 2, rect.height - 2
            )
            # 繪製圓角矩形
            pygame.draw.rect(self.game_surface, segment_color, inner_rect, border_radius=min(8, GRID_SIZE // 6))

            # 如果是蛇頭 (i == 0)，繪製眼睛
            if i == 0:
                eye_size = max(4, GRID_SIZE // 10) # 眼睛大小
                eye_offset = GRID_SIZE // 4 # 眼睛偏移量
                # 根據假設的蛇頭朝向計算眼睛位置 (這裡假設朝左)
                left_eye = (rect.x + eye_offset, rect.y + eye_offset)
                right_eye = (rect.x + eye_offset, rect.y + GRID_SIZE - eye_offset - eye_size)
                # 繪製黑色眼睛
                pygame.draw.rect(self.game_surface, BLACK, (*left_eye, eye_size, eye_size))
                pygame.draw.rect(self.game_surface, BLACK, (*right_eye, eye_size, eye_size))

    # 將固定大小的遊戲 Surface 內容縮放並繪製到可變大小的主視窗上，保持寬高比
    def draw_scaled_surface(self):
        """縮放遊戲 Surface 並繪製到主視窗上"""
        window_width, window_height = self.screen.get_size() # 獲取當前視窗大小
        aspect_ratio = GAME_WIDTH / GAME_HEIGHT # 遊戲內容寬高比
        # 計算縮放後的尺寸，保持寬高比並填滿視窗的某個維度
        if window_width / window_height >= aspect_ratio:
            # 視窗較寬，以高度為基準
            scale_h = window_height
            scale_w = int(scale_h * aspect_ratio)
        else:
            # 視窗較高，以寬度為基準
            scale_w = window_width
            scale_h = int(scale_w / aspect_ratio)
        # 縮放 game_surface
        scaled_surface = pygame.transform.scale(self.game_surface, (scale_w, scale_h))
        scaled_rect = scaled_surface.get_rect() # 獲取縮放後的矩形區域
        # 將縮放後的 Surface 置於視窗中央
        scaled_rect.center = (window_width // 2, window_height // 2)
        self.screen.fill(BLACK) # 用黑色填充視窗背景 (處理黑邊)
        self.screen.blit(scaled_surface, scaled_rect) # 將縮放後的 Surface 繪製到視窗上

    # 更新遊戲狀態，主要處理倒數計時邏輯和觸發遊戲邏輯更新
    def update(self):
        """更新遊戲狀態"""
        # 如果是倒數計時狀態
        if self.state == "countdown":
            current_time = pygame.time.get_ticks() # 獲取當前時間
            elapsed_time = current_time - self.countdown_start_time # 計算經過時間
            # 根據經過時間更新倒數數字
            if elapsed_time <= 1000:
                self.countdown_number = 3
            elif elapsed_time <= 2000:
                self.countdown_number = 2
            elif elapsed_time <= self.countdown_duration:
                self.countdown_number = 1
            else:
                # 倒數結束，切換到遊戲狀態
                self.state = "game"
                self.game.game_active = True # 啟動遊戲邏輯
        # 如果是遊戲狀態
        elif self.state == "game":
            self.game.update() # 調用 Game 物件的 update 方法處理遊戲邏輯

    # 繪製倒數計時畫面
    def draw_countdown(self):
        """繪製倒數畫面"""
        self.game.draw_background() # 繪製背景
        # 繪製蛇和食物的靜態畫面
        for snake in self.game.snakes:
            snake.draw(self.game_surface)
        for food in self.game.foods:
            food.draw(self.game_surface)
        # 繪製半透明疊加層
        overlay = pygame.Surface((GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150)) # 黑色，較高透明度
        self.game_surface.blit(overlay, (0, 0))
        # 繪製倒數數字
        countdown_text = str(self.countdown_number)
        text_surface = self.countdown_font.render(countdown_text, True, WHITE)
        text_rect = text_surface.get_rect(center=(GAME_WIDTH // 2, GAME_HEIGHT // 2))
        # 繪製數字陰影
        shadow_offset = 5
        shadow_color = (0, 0, 0, 200)
        shadow_surf = self.countdown_font.render(countdown_text, True, shadow_color)
        shadow_rect = shadow_surf.get_rect(center=(text_rect.centerx + shadow_offset, text_rect.centery + shadow_offset))
        self.game_surface.blit(shadow_surf, shadow_rect)
        # 繪製數字本身
        self.game_surface.blit(text_surface, text_rect)

    # 根據當前遊戲狀態調用相應的繪製方法，並將最終畫面更新到螢幕
    def draw(self):
        """繪製遊戲畫面"""
        if self.state == "menu":
            self.draw_menu() # 繪製主選單
        elif self.state == "countdown":
            self.draw_countdown() # 繪製倒數畫面
        elif self.state == "game":
            self.game.draw() # 調用 Game 物件的 draw 方法繪製遊戲內容
        # 將 game_surface 的內容縮放並繪製到主視窗 screen 上
        self.draw_scaled_surface()
        pygame.display.flip() # 更新整個螢幕顯示

    # 清理 Pygame 資源並退出程式
    def quit_game(self):
        """關閉並退出遊戲"""
        pygame.quit() # 卸載 Pygame 模組
        sys.exit() # 退出 Python 程式

    # 遊戲的主迴圈
    def run(self):
        """遊戲主迴圈"""
        while True:
            self.handle_events() # 處理事件
            self.update() # 更新遊戲狀態
            self.draw() # 繪製畫面
            self.clock.tick(SNAKE_SPEED) # 控制遊戲迴圈的幀率

# 程式執行入口
if __name__ == "__main__":
    game = SnakeGame() # 創建 SnakeGame 實例
    game.run() # 開始遊戲主迴圈
