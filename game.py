import pygame
import os
import math
import random
from settings import *
from objects import Snake, Food, AISnake

# 遊戲邏輯類別，負責處理蛇的移動、碰撞、食物生成、分數計算等
class Game:
    # 初始化遊戲物件，包括螢幕、遊戲繪圖表面、音效、模式、蛇列表、食物列表等
    def __init__(self, screen, surface, sounds):
        self.screen = screen # 主視窗 Surface，用於最終顯示
        self.game_surface = surface # 遊戲內容繪製的 Surface，固定大小
        self.sounds = sounds # 從 SnakeGame 傳入的音效字典
        self.mode = "single" # 預設遊戲模式為單人
        self.snakes = [] # 儲存所有蛇物件 (玩家或 AI) 的列表
        self.foods = [] # 儲存所有食物物件的列表
        self.game_active = False # 標記遊戲邏輯是否正在運行 (True 為遊戲中, False 為選單/結束/倒數)
        self.game_paused = False # 標記遊戲是否被玩家暫停
        self.winner_message = "" # 遊戲結束時顯示的勝利/失敗/平局訊息
        self.create_fonts() # 初始化載入遊戲內所需的字體

    # 載入遊戲中顯示分數和遊戲結束訊息所需的字體
    def create_fonts(self):
        """加載字體"""
        try:
            # 檢查自訂字體檔案是否存在
            if not os.path.exists(FONT_PATH):
                raise FileNotFoundError(f"找不到字體檔案: {FONT_PATH}") # 拋出檔案未找到錯誤
            # 載入分數和遊戲結束畫面的字體，使用指定的路徑和大小
            self.score_font = pygame.font.Font(FONT_PATH, SCORE_FONT_SIZE)
            self.game_over_font = pygame.font.Font(FONT_PATH, GAME_OVER_FONT_SIZE)
        except Exception as e: # 捕獲所有可能的異常 (檔案找不到、字體損壞等)
            # 處理自訂字體載入錯誤
            print(f"無法載入自訂字體: {e}")
            try:
                # 嘗試獲取系統可用字體列表
                available_fonts = pygame.font.get_fonts()
                if available_fonts: # 如果系統中存在可用字體
                    # 使用列表中的第一個系統字體作為備選
                    system_font = available_fonts[0]
                    self.score_font = pygame.font.SysFont(system_font, SCORE_FONT_SIZE)
                    self.game_over_font = pygame.font.SysFont(system_font, GAME_OVER_FONT_SIZE)
                else: # 如果連系統字體都沒有
                    # 使用 Pygame 的預設字體 (通常是 sans-serif)
                    self.score_font = pygame.font.Font(None, SCORE_FONT_SIZE)
                    self.game_over_font = pygame.font.Font(None, GAME_OVER_FONT_SIZE)
            except Exception: # 如果載入系統字體也失敗
                # 最後的保險措施：使用 Pygame 預設字體
                self.score_font = pygame.font.Font(None, SCORE_FONT_SIZE)
                self.game_over_font = pygame.font.Font(None, GAME_OVER_FONT_SIZE)

    # 根據指定的遊戲模式重置遊戲狀態，清除蛇和食物，重新生成物件
    def reset_game(self, mode="single"):
        """根據模式重置遊戲狀態"""
        self.stop_sound('gameover') # 確保停止上局可能播放的遊戲結束音效
        self.mode = mode # 設定當前遊戲模式 ('single', 'multi', 'ai')
        self.snakes = [] # 清空蛇列表
        self.foods = [] # 清空食物列表
        self.winner_message = "" # 清空上一局的勝利訊息
        self.game_active = False # 遊戲尚未開始，邏輯不活躍
        self.game_paused = False # 重置暫停狀態
        self.game_over_sound_played = False # 重置遊戲結束音效播放標記

        # 根據不同的遊戲模式，創建不同組合的蛇物件
        if self.mode == "single":
            # 單人模式：創建一條玩家蛇，位於左側，向右移動，綠色
            self.snakes.append(Snake(player_id=1, start_pos=(GRID_WIDTH // 4, GRID_HEIGHT // 2), start_dir=(1, 0), color_config=(GREEN, DARK_GREEN)))
        elif self.mode == "multi":
            # 雙人模式：創建兩條玩家蛇，分別位於左右兩側，相向移動，不同顏色
            self.snakes.append(Snake(player_id=1, start_pos=(GRID_WIDTH // 4, GRID_HEIGHT // 2), start_dir=(1, 0), color_config=(GREEN, DARK_GREEN))) # 玩家1
            self.snakes.append(Snake(player_id=2, start_pos=(GRID_WIDTH * 3 // 4, GRID_HEIGHT // 2), start_dir=(-1, 0), color_config=(BLUE, DARK_BLUE))) # 玩家2
        elif self.mode == "ai":
            # 電腦對戰模式：創建一條玩家蛇和一條 AI 蛇，配置同雙人模式
            self.snakes.append(Snake(player_id=1, start_pos=(GRID_WIDTH // 4, GRID_HEIGHT // 2), start_dir=(1, 0), color_config=(GREEN, DARK_GREEN))) # 玩家1
            self.snakes.append(AISnake(player_id=2, start_pos=(GRID_WIDTH * 3 // 4, GRID_HEIGHT // 2), start_dir=(-1, 0), color_config=(BLUE, DARK_BLUE))) # AI 玩家

        # 在場景中生成初始數量的食物
        self.spawn_initial_foods()

    # 生成遊戲開始時的初始食物
    def spawn_initial_foods(self):
        """生成初始數量的食物"""
        # 根據遊戲模式決定場上最多允許存在的食物數量
        max_foods = MAX_FOOD_SINGLE if self.mode == "single" else MAX_FOOD_MULTI
        # 創建一個集合，用於儲存所有已被蛇佔據的初始位置
        occupied_positions = set()
        for snake in self.snakes:
            occupied_positions.update(snake.positions) # 將蛇的初始位置加入集合
        # 迴圈生成食物，直到達到該模式下的最大食物數量
        while len(self.foods) < max_foods:
            self.spawn_new_food(occupied_positions) # 呼叫生成單個食物的方法

    # 在隨機未被佔用的位置生成一個新的食物
    def spawn_new_food(self, occupied_positions):
        """根據概率生成一個新的食物"""
        # 根據 settings.py 中定義的食物類型和概率，隨機選擇一種食物
        # random.choices 返回一個列表，取第一個元素 [0]
        chosen_type_data = random.choices(FOOD_TYPES, weights=FOOD_PROBABILITIES, k=1)[0]
        # 創建 Food 物件實例，傳入已佔用位置集合以避免生成在蛇身上或已有食物上
        new_food = Food(occupied_positions, chosen_type_data)
        self.foods.append(new_food) # 將新生成的食物加入食物列表
        occupied_positions.add(new_food.position) # 將新食物的位置也加入已佔用位置集合 (供下一次生成參考)

    # 播放指定名稱的音效 (如果音效已載入且存在於字典中)
    def play_sound(self, sound_name):
        """播放指定音效"""
        # 檢查 self.sounds 是否存在，音效名稱是否存在於字典中，以及對應的值是否為有效的 Sound 物件
        if self.sounds and sound_name in self.sounds and self.sounds[sound_name]:
            self.sounds[sound_name].play() # 播放音效

    # 停止指定名稱的音效 (如果音效已載入且存在於字典中)
    def stop_sound(self, sound_name):
        """停止指定音效"""
        # 檢查條件同 play_sound
        if self.sounds and sound_name in self.sounds and self.sounds[sound_name]:
            self.sounds[sound_name].stop() # 停止音效

    # 處理遊戲進行中的事件，主要是玩家的按鍵輸入
    def handle_events(self, events):
        """處理遊戲事件，支持雙人控制"""
        for event in events: # 遍歷從主循環傳遞過來的事件列表
            if event.type == pygame.KEYDOWN: # 只關心按鍵按下的事件
                if self.game_active: # 確保遊戲正在進行中 (不是結束畫面或倒計時)
                    # 檢查是否按下 P 鍵，用於暫停/繼續
                    if event.key == pygame.K_p:
                        self.game_paused = not self.game_paused # 切換暫停狀態
                        continue # 處理完畢，跳過此事件的後續處理

                    # 如果遊戲未處於暫停狀態，則處理玩家的移動控制
                    if not self.game_paused:
                        # 處理玩家 1 的控制 (上下左右方向鍵)
                        # 檢查蛇列表中是否存在第一條蛇，並且該蛇不是 AI 蛇
                        if len(self.snakes) > 0 and not isinstance(self.snakes[0], AISnake):
                            # 檢查按下的鍵是否在玩家 1 的控制映射中定義
                            if event.key in PLAYER1_CONTROLS:
                                # 呼叫第一條蛇的 turn 方法，傳入對應的方向向量
                                self.snakes[0].turn(PLAYER1_CONTROLS[event.key])

                        # 處理玩家 2 的控制 (WASD 鍵)
                        # 檢查是否為雙人模式，蛇列表中是否存在第二條蛇，並且該蛇不是 AI 蛇
                        if self.mode == "multi" and len(self.snakes) > 1 and not isinstance(self.snakes[1], AISnake):
                            # 檢查按下的鍵是否在玩家 2 的控制映射中定義
                            if event.key in PLAYER2_CONTROLS:
                                # 呼叫第二條蛇的 turn 方法，傳入對應的方向向量
                                self.snakes[1].turn(PLAYER2_CONTROLS[event.key])

    # 更新遊戲的邏輯狀態，包括 AI 決策、蛇的移動、碰撞檢測、食物處理等
    def update(self):
        """更新遊戲狀態"""
        # 如果遊戲未開始 (game_active is False) 或已暫停 (game_paused is True)，則不進行任何邏輯更新
        if not self.game_active or self.game_paused:
            return # 直接返回，跳過後續更新步驟

        # 讓所有 AI 蛇決定下一步的移動方向
        for snake in self.snakes:
            # 檢查蛇是否為 AISnake 的實例並且還活著
            if isinstance(snake, AISnake) and not snake.is_dead:
                # 呼叫 AI 蛇的決策方法，傳入當前的食物列表和其他蛇的列表作為參考
                snake.decide_direction(self.foods, self.snakes)

        # 移動所有活著的蛇 (包括玩家和 AI)
        for snake in self.snakes:
            if not snake.is_dead: # 只移動活著的蛇
                move_success = snake.move() # 呼叫蛇自身的 move 方法嘗試移動
                if not move_success: # 如果 move 方法返回 False (表示撞牆或撞自身)
                    snake.die() # 將這條蛇標記為死亡狀態

        # 檢查各種碰撞情況 (蛇撞蛇、頭對頭碰撞等)
        self.check_collisions()

        # 碰撞檢測後，遊戲狀態可能變為非活躍 (game_active=False)
        if not self.game_active:
            # 如果遊戲剛剛結束，並且遊戲結束音效還沒播放過
            if not self.game_over_sound_played:
                self.play_sound('gameover') # 播放遊戲結束音效
                self.game_over_sound_played = True # 標記已播放，防止重複播放
            return # 遊戲已結束，不需要再處理食物邏輯，直接返回

        # 如果遊戲仍然活躍，處理蛇吃食物的邏輯
        self.handle_food_eating()
        # 處理食物超時消失的邏輯
        self.handle_food_timeout()

    # 獲取當前所有被蛇身體和食物佔據的格子位置集合
    def get_all_occupied_positions(self):
        """獲取所有被蛇和食物佔據的位置"""
        occupied = set() # 使用集合可以自動去重，並且查找效率高
        # 遍歷所有蛇
        for snake in self.snakes:
            occupied.update(snake.positions) # 將蛇的所有身體部分的座標加入集合
        # 遍歷所有食物
        for food in self.foods:
            occupied.add(food.position) # 將食物的座標加入集合
        return occupied # 返回包含所有佔用位置的集合

    # 處理蛇吃到食物的邏輯：蛇增長、播放音效、移除食物、生成新食物
    def handle_food_eating(self):
        """處理蛇吃食物的邏輯"""
        eaten_foods_indices = [] # 用於儲存本輪被吃掉的食物在 self.foods 列表中的索引
        # 遍歷食物列表，獲取索引 i 和食物物件 food
        for i, food in enumerate(self.foods):
            # 對於每個食物，遍歷所有蛇
            for snake in self.snakes:
                # 檢查蛇是否活著，以及蛇頭的位置是否與當前食物的位置相同
                if not snake.is_dead and snake.get_head_position() == food.position:
                    snake.grow(food.score) # 呼叫蛇的 grow 方法，傳入食物的分值 (可能為負)
                    self.play_sound('eating') # 播放吃東西的音效
                    eaten_foods_indices.append(i) # 將該食物的索引記錄下來
                    break # 一個食物只能被一條蛇吃，找到吃的蛇後跳出內層循環，檢查下一個食物

        # 如果本輪有食物被吃掉
        if eaten_foods_indices:
            # 重新計算當前所有被佔用的位置 (因為蛇可能增長了)
            occupied_positions = self.get_all_occupied_positions()
            # 從後往前遍歷被吃掉食物的索引列表，這樣刪除元素時不會影響前面元素的索引
            for index in sorted(eaten_foods_indices, reverse=True):
                eaten_food_pos = self.foods[index].position # 獲取被吃食物的位置
                # 從佔用位置集合中移除該位置 (如果存在的話)
                if eaten_food_pos in occupied_positions:
                    occupied_positions.remove(eaten_food_pos)
                del self.foods[index] # 從食物列表中刪除該食物物件
            # 根據遊戲模式確定場上應有的最大食物數
            max_foods = MAX_FOOD_SINGLE if self.mode == "single" else MAX_FOOD_MULTI
            # 持續生成新食物，直到場上食物數量達到最大值
            while len(self.foods) < max_foods:
                self.spawn_new_food(occupied_positions) # 傳入更新後的佔用位置集合

    # 處理食物因超時而消失的邏輯
    def handle_food_timeout(self):
        """處理食物超時邏輯"""
        timed_out_foods_indices = [] # 用於儲存本輪超時消失的食物索引
        # 遍歷所有食物
        for i, food in enumerate(self.foods):
            # 呼叫食物自身的 is_timed_out 方法檢查是否超時
            if food.is_timed_out():
                timed_out_foods_indices.append(i) # 如果超時，記錄索引

        # 如果本輪有食物超時
        if timed_out_foods_indices:
            # 重新獲取當前所有佔用位置 (雖然食物消失不會改變蛇的位置，但保持一致性)
            occupied_positions = self.get_all_occupied_positions()
            # 從後往前遍歷超時食物的索引列表
            for index in sorted(timed_out_foods_indices, reverse=True):
                timed_out_food_pos = self.foods[index].position # 獲取超時食物的位置
                # 從佔用位置集合中移除該位置
                if timed_out_food_pos in occupied_positions:
                    occupied_positions.remove(timed_out_food_pos)
                del self.foods[index] # 從食物列表中刪除該食物物件
            # 根據模式確定最大食物數
            max_foods = MAX_FOOD_SINGLE if self.mode == "single" else MAX_FOOD_MULTI
            # 持續生成新食物，補充因超時消失的食物，直到達到最大值
            while len(self.foods) < max_foods:
                self.spawn_new_food(occupied_positions)

    # 繪製遊戲的主要畫面內容
    def draw(self):
        """繪製遊戲畫面"""
        self.draw_background() # 首先繪製棋盤格背景
        # 遍歷所有蛇並呼叫它們的 draw 方法
        for snake in self.snakes:
            snake.draw(self.game_surface)
        # 遍歷所有食物並呼叫它們的 draw 方法
        for food in self.foods:
            food.draw(self.game_surface)
        # 在遊戲元素上方繪製分數顯示
        self.draw_score()
        # 如果遊戲已結束 (非活躍狀態)
        if not self.game_active:
            self.draw_game_over() # 繪製遊戲結束的疊加畫面
        # 如果遊戲處於暫停狀態
        elif self.game_paused:
            self.draw_paused() # 繪製遊戲暫停的疊加畫面
        # 注意：所有繪製操作都是在 self.game_surface 上進行

    # 繪製棋盤格背景
    def draw_background(self):
        """繪製棋盤格背景"""
        # 遍歷遊戲區域的每一個格子
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                # 計算當前格子的矩形區域 (像素座標)
                rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
                # 根據格子座標 (x+y) 的奇偶性決定顏色
                if (x + y) % 2 == 0: # 偶數格子
                    pygame.draw.rect(self.game_surface, CHECKERBOARD_COLOR_1, rect) # 繪製顏色 1
                else: # 奇數格子
                    pygame.draw.rect(self.game_surface, CHECKERBOARD_COLOR_2, rect) # 繪製顏色 2

    # 在遊戲畫面上繪製分數
    def draw_score(self):
        """繪製分數，支持多玩家"""
        start_y = 10 # 第一行分數文字的起始 Y 座標 (距離頂部邊緣)
        # 遍歷蛇列表，為每條蛇顯示分數
        for i, snake in enumerate(self.snakes):
            # 根據蛇的類型和遊戲模式確定玩家標籤
            player_label = f"玩家 {snake.player_id}" # 預設標籤
            if isinstance(snake, AISnake): # 如果是 AI 蛇
                player_label = "電腦"
            elif self.mode == "single": # 如果是單人模式
                 player_label = "分數" # 只顯示 "分數"
            # 組合最終要顯示的文字
            score_text = f"{player_label}: {snake.score}"
            # 使用蛇的身體顏色作為文字顏色，以區分不同玩家的分數
            text_color = snake.body_color

            # 繪製文字陰影以增加可讀性
            shadow_offset = 2 # 陰影偏移量
            shadow_color = (0, 0, 0, 180) # 半透明黑色
            # 渲染陰影文字 Surface
            shadow_surface = self.score_font.render(score_text, False, shadow_color)
            # 計算陰影文字的位置 (向右下偏移)
            shadow_rect = shadow_surface.get_rect(topleft=(10 + shadow_offset, start_y + shadow_offset))
            # 繪製陰影
            self.game_surface.blit(shadow_surface, shadow_rect)

            # 渲染實際分數文字 Surface
            text_surface = self.score_font.render(score_text, False, text_color)
            # 計算實際文字的位置 (左上角對齊)
            text_rect = text_surface.get_rect(topleft=(10, start_y))
            # 繪製實際文字
            self.game_surface.blit(text_surface, text_rect)
            # 為下一行分數更新起始 Y 座標
            start_y += text_rect.height + 5 # 增加文字高度和一點間距

    # 繪製遊戲結束畫面
    def draw_game_over(self):
        """繪製遊戲結束畫面"""
        # 創建一個與遊戲區域同樣大小的半透明 Surface 作為疊加層
        overlay = pygame.Surface((GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA) # SRCALPHA 支持透明度
        overlay.fill(OVERLAY_COLOR) # 填充預設的疊加顏色 (settings.py)
        self.game_surface.blit(overlay, (0, 0)) # 將疊加層繪製在最上方

        # 準備遊戲結束的文字內容
        # 如果有勝利者訊息，則顯示；否則顯示通用的 "遊戲結束!"
        game_over_text1 = self.winner_message if self.winner_message else "遊戲結束!"
        game_over_text3 = "按任意鍵返回主畫面" # 提示玩家操作

        # 使用較大的字體渲染標題文字
        text1_surface = self.game_over_font.render(game_over_text1, False, BRIGHT_RED) # 使用亮紅色
        # 使用分數的字體渲染提示文字
        text3_surface = self.score_font.render(game_over_text3, False, TEXT_COLOR) # 使用標準文字顏色
        # 計算標題和提示文字的位置，使其水平居中
        text1_rect = text1_surface.get_rect(center=(GAME_WIDTH // 2, GAME_HEIGHT // 2 - 60)) # 標題偏上
        text3_rect = text3_surface.get_rect(center=(GAME_WIDTH // 2, GAME_HEIGHT // 2 + 100)) # 提示偏下

        # 繪製標題文字陰影
        shadow_offset = 2
        shadow_color = (0, 0, 0, 200) # 陰影顏色可以比分數的更深
        shadow_surf1 = self.game_over_font.render(game_over_text1, False, shadow_color)
        shadow_rect1 = shadow_surf1.get_rect(center=(text1_rect.centerx + shadow_offset, text1_rect.centery + shadow_offset))
        self.game_surface.blit(shadow_surf1, shadow_rect1)
        # 繪製標題文字本身
        self.game_surface.blit(text1_surface, text1_rect)

        # 在標題下方顯示每條蛇的最終分數
        start_y = text1_rect.bottom + 20 # 計算分數顯示的起始 Y 座標
        for i, snake in enumerate(self.snakes):
            # 確定玩家標籤
            player_label = f"玩家 {snake.player_id}"
            if isinstance(snake, AISnake):
                player_label = "電腦"
            elif self.mode == "single":
                 player_label = "最終分數" # 單人模式下顯示 "最終分數"
            score_text = f"{player_label}: {snake.score}" # 組合分數文字
            text_color = snake.body_color # 文字顏色同蛇身

            # 繪製分數陰影
            score_shadow_surface = self.score_font.render(score_text, False, shadow_color)
            score_shadow_rect = score_shadow_surface.get_rect(center=(GAME_WIDTH // 2 + shadow_offset, start_y + shadow_offset)) # 水平居中並偏移
            self.game_surface.blit(score_shadow_surface, score_shadow_rect)
            # 繪製分數文字
            score_surface = self.score_font.render(score_text, False, text_color)
            score_rect = score_surface.get_rect(center=(GAME_WIDTH // 2, start_y)) # 水平居中
            self.game_surface.blit(score_surface, score_rect)
            # 更新下一行分數的 Y 座標
            start_y += score_rect.height + 10

        # 在所有分數下方繪製返回主畫面的提示文字
        self.game_surface.blit(text3_surface, text3_rect)

    # 繪製遊戲暫停時的畫面
    def draw_paused(self):
        """繪製遊戲暫停畫面"""
        # 創建半透明疊加層
        overlay = pygame.Surface((GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 20, 150)) # 使用稍微不同的顏色或透明度與遊戲結束區分
        self.game_surface.blit(overlay, (0, 0))

        # 準備文字內容
        paused_text = "遊戲暫停"
        continue_text = "按 P 繼續"

        # 渲染文字
        text1_surface = self.game_over_font.render(paused_text, False, TITLE_COLOR) # 使用主選單標題顏色
        text2_surface = self.score_font.render(continue_text, False, HIGHLIGHT_COLOR) # 使用高亮顏色

        # 計算文字位置 (居中)
        text1_rect = text1_surface.get_rect(center=(GAME_WIDTH // 2, GAME_HEIGHT // 2 - 40)) # 暫停標題偏上
        text2_rect = text2_surface.get_rect(center=(GAME_WIDTH // 2, GAME_HEIGHT // 2 + 40)) # 繼續提示偏下

        # 使 "按 P 繼續" 文字產生閃爍效果
        current_time = pygame.time.get_ticks() # 獲取當前時間
        # 使用正弦函數來回改變透明度 (alpha 值)
        alpha = int(127 + 127 * abs(math.sin(current_time * 0.002))) # alpha 在 0 到 254 之間變化
        text2_surface.set_alpha(alpha) # 設定文字 Surface 的透明度

        # 繪製文字
        self.game_surface.blit(text1_surface, text1_rect)
        self.game_surface.blit(text2_surface, text2_rect)

    # 檢查遊戲中的各種碰撞情況，包括蛇撞蛇、蛇撞自己、蛇頭對撞
    # 注意：蛇撞牆和撞自己的邏輯已在 Snake.move() 中處理，這裡主要處理蛇與蛇之間的碰撞
    def check_collisions(self):
        """檢查碰撞，處理獲勝/失敗/平手條件"""
        # 如果遊戲邏輯未激活 (例如在選單或結束畫面)，則不進行碰撞檢測
        if not self.game_active:
            return

        # 特殊處理 AI 模式：如果玩家蛇已經死亡，直接判定電腦獲勝，結束遊戲
        if self.mode == "ai":
            # 使用 next 查找第一條非 AI 且已死亡的蛇，如果找不到則返回 None
            player_snake = next((s for s in self.snakes if not isinstance(s, AISnake) and s.is_dead), None)
            if player_snake: # 如果找到了死掉的玩家蛇
                self.end_game("電腦獲勝!") # 呼叫結束遊戲方法
                return # 不再進行後續的碰撞檢測

        # --- 廣泛碰撞檢測 --- #
        # 獲取當前所有還活著的蛇的列表
        live_snakes = [s for s in self.snakes if not s.is_dead]
        # 用於儲存本輪因碰撞確定要死亡的蛇在 live_snakes 列表中的索引
        collided_indices = set()
        # 創建一個字典，用於儲存所有蛇的身體部分 (不包括頭部) 的座標及其對應的蛇在 self.snakes 中的原始索引
        all_body_parts = {}

        # 填充 all_body_parts 字典
        for i, snake in enumerate(self.snakes): # 遍歷所有蛇 (包括可能已死的，雖然死的蛇身體不應該造成碰撞)
            if not snake.is_dead: # 只考慮活蛇的身體
                 # 遍歷蛇的身體部分 (從索引 1 開始，跳過頭部)
                 for part in snake.positions[1:]:
                     all_body_parts[part] = i # 將座標作為 key，蛇的原始索引作為 value

        # 1. 檢查蛇頭是否撞到其他蛇的身體
        for i, snake in enumerate(live_snakes): # 遍歷所有活蛇
            head = snake.get_head_position() # 獲取當前活蛇的頭部座標
            # 檢查頭部座標是否存在於身體部位字典中
            if head in all_body_parts:
                collided_snake_index = all_body_parts[head] # 獲取被撞身體部位所屬蛇的原始索引
                original_collided_snake = self.snakes[collided_snake_index] # 獲取被撞的蛇物件
                # 確保不是撞到自己的身體 (雖然 move 裡有檢查，這裡再確認一次更保險)
                if snake != original_collided_snake:
                     # 如果頭撞到了別的蛇的身體，那麼這條蛇 (snake) 死亡
                     collided_indices.add(i) # 將當前蛇在 live_snakes 中的索引加入待死亡集合

        # 2. 檢查蛇頭對撞 (Head-on collision)
        head_positions = {} # 創建一個字典，用於記錄每個格子座標上有哪些活蛇的頭部
        for i, snake in enumerate(live_snakes): # 遍歷所有活蛇
            head = snake.get_head_position() # 獲取頭部座標
            if head not in head_positions: # 如果該座標是第一次出現
                head_positions[head] = [] # 初始化一個空列表
            head_positions[head].append(i) # 將當前蛇在 live_snakes 中的索引加入該座標的列表

        # 處理記錄下來的頭部位置信息
        for head, indices in head_positions.items(): # 遍歷每個頭部座標和佔據該座標的活蛇索引列表
            if len(indices) > 1: # 如果同一個格子上有超過一條蛇的頭 (發生了頭對頭碰撞)
                # 獲取所有在該點碰撞的活蛇物件
                colliding_live_snakes = [live_snakes[i] for i in indices]
                max_score = -1 # 初始化最高分數為 -1
                winners = [] # 用於記錄分數最高的蛇 (可能不止一條)

                # 找出碰撞蛇中分數最高的蛇
                for s in colliding_live_snakes:
                    if s.score > max_score: # 如果當前蛇分數更高
                        max_score = s.score # 更新最高分
                        winners = [s] # 重置勝利者列表
                    elif s.score == max_score: # 如果分數與當前最高分相同
                        winners.append(s) # 加入勝利者列表 (平局)

                # 根據勝利者數量決定誰死亡
                if len(winners) == 1: # 如果只有一個最高分 (只有一個勝利者)
                    winner_snake = winners[0] # 獲取勝利的蛇
                    # 所有參與碰撞但不是勝利者的蛇都死亡
                    for i in indices:
                        if live_snakes[i] != winner_snake:
                            collided_indices.add(i) # 將其索引加入待死亡集合
                else: # 如果有多個最高分 (平局)
                    # 所有參與頭對頭碰撞的蛇都死亡
                    for i in indices:
                        collided_indices.add(i) # 將所有參與碰撞的索引加入待死亡集合

        # --- 處理碰撞結果 --- #
        # 如果 collided_indices 集合不為空，表示本輪有蛇因碰撞死亡
        if collided_indices:
            # 需要從 live_snakes 列表中移除這些蛇，並在 self.snakes 中標記它們為死亡
            indices_to_kill = set() # 用於儲存需要在 self.snakes 中標記死亡的蛇的原始索引
            # 對 collided_indices (是 live_snakes 的索引) 進行排序，從後往前處理，避免索引問題
            sorted_collided_indices = sorted(list(collided_indices), reverse=True)
            for live_idx in sorted_collided_indices:
                 # 確保索引有效 (理論上應該總是有效)
                 if live_idx < len(live_snakes):
                     # 從 live_snakes 彈出確定要死亡的蛇物件 (這步修改了 live_snakes，但不影響後續循環，因為是從後往前)
                     # 這行其實可以省略，因為後面會重新生成 live_snakes
                     snake_to_die = live_snakes.pop(live_idx) # 獲取要死的蛇物件
                     # 找到這條蛇在原始 self.snakes 列表中的索引
                     original_idx = self.snakes.index(snake_to_die)
                     indices_to_kill.add(original_idx) # 記錄原始索引

            # 根據記錄的原始索引，在 self.snakes 中將對應的蛇標記為死亡
            for original_idx in indices_to_kill:
                 self.snakes[original_idx].die()

            # 在處理完所有碰撞死亡後，重新生成最新的活蛇列表
            live_snakes = [s for s in self.snakes if not s.is_dead]

        # --- 根據模式判斷遊戲是否結束 --- #
        if self.mode == "single":
            # 單人模式：如果 live_snakes 為空 (唯一的蛇死了)
            if not live_snakes:
                self.end_game("遊戲結束!") # 結束遊戲
            return # 單人模式的碰撞處理到此結束

        elif self.mode == "multi":
            # 雙人模式：如果活蛇數量小於等於 1 (表示有勝負或平局)
            if len(live_snakes) <= 1:
                if len(live_snakes) == 0: # 如果沒有活蛇了 (兩條都死了)
                    # 需要根據分數和死亡時間判斷勝負
                    # 獲取玩家 1 的分數，如果列表不存在則設為 -1
                    score1 = self.snakes[0].score if len(self.snakes) > 0 else -1
                    # 獲取玩家 2 的分數
                    score2 = self.snakes[1].score if len(self.snakes) > 1 else -1
                    # 獲取玩家 1 的死亡時間，如果未死或不存在則設為無窮大
                    time1 = self.snakes[0].death_time if len(self.snakes) > 0 and self.snakes[0].death_time is not None else float('inf')
                    # 獲取玩家 2 的死亡時間
                    time2 = self.snakes[1].death_time if len(self.snakes) > 1 and self.snakes[1].death_time is not None else float('inf')

                    # 比較分數決定勝負
                    if score1 > score2:
                        self.end_game("玩家 1 獲勝!")
                    elif score2 > score1:
                        self.end_game("玩家 2 獲勝!")
                    else: # 分數相同，比較死亡時間
                        # 活得更久的獲勝 (死亡時間戳更大)
                        if time1 > time2: # 玩家1 後死
                            self.end_game("玩家 1 獲勝!")
                        elif time2 > time1: # 玩家2 後死
                            self.end_game("玩家 2 獲勝!")
                        else: # 分數和死亡時間都相同 (極少情況，例如同時撞牆)
                            self.end_game("平局!")
                elif len(live_snakes) == 1: # 如果還剩下一條活蛇
                     winner = live_snakes[0] # 剩下的就是勝利者
                     self.end_game(f"玩家 {winner.player_id} 獲勝!") # 宣布勝利者
            return # 雙人模式的碰撞處理到此結束

        elif self.mode == "ai":
            # AI 模式：(玩家死亡情況已在開頭處理)
            # 查找玩家蛇和 AI 蛇物件
            player_snake = next((s for s in self.snakes if not isinstance(s, AISnake)), None)
            ai_snake = next((s for s in self.snakes if isinstance(s, AISnake)), None)

            # 如果 AI 蛇死亡，並且玩家蛇還活著
            if ai_snake and ai_snake.is_dead and player_snake and not player_snake.is_dead:
                self.end_game("玩家獲勝!") # 玩家獲勝
            # 如果兩者都死亡了
            elif not live_snakes:
                 # 比較分數決定勝負 (類似雙人模式，但標籤不同)
                 player_score = player_snake.score if player_snake else -1
                 ai_score = ai_snake.score if ai_snake else -1
                 if player_score > ai_score:
                     self.end_game("玩家獲勝!")
                 elif ai_score > player_score:
                     self.end_game("電腦獲勝!")
                 else: # 分數相同，比較死亡時間
                     player_time = player_snake.death_time if player_snake and player_snake.death_time is not None else float('inf')
                     ai_time = ai_snake.death_time if ai_snake and ai_snake.death_time is not None else float('inf')
                     if player_time > ai_time: # 玩家活得久
                         self.end_game("玩家獲勝!")
                     elif ai_time > player_time: # AI 活得久
                         self.end_game("電腦獲勝!")
                     else: # 都相同
                         self.end_game("平局!")
            # 如果只剩下 AI 蛇活著 (玩家蛇已死)，這種情況已在開頭處理
            # 如果只剩下玩家蛇活著 (AI 蛇已死)，則上面已處理
            return # AI 模式的碰撞處理到此結束


    # 結束當前遊戲，設定結束原因 (勝利訊息) 並標記遊戲為非活躍狀態
    def end_game(self, reason):
        """結束遊戲並記錄原因"""
        # 確保遊戲當前是活躍的，避免重複結束
        if self.game_active:
            self.game_active = False # 將遊戲標記為非活躍狀態
            self.winner_message = reason # 儲存結束的原因/勝利訊息，用於顯示在結束畫面上
            # 播放遊戲結束音效 (如果還沒播放過)
            if not self.game_over_sound_played:
                self.play_sound('gameover')
                self.game_over_sound_played = True
