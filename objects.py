import pygame
import random
import os
import math                
from settings import *

# 代表遊戲中蛇的類別
class Snake:
    # 初始化蛇的屬性
    def __init__(self, player_id, start_pos, start_dir, color_config):
        self.player_id = player_id # 玩家 ID (用於區分玩家或 AI)
        self.length = 1 # 初始長度
        self.positions = [start_pos] # 蛇身體佔據的格子座標列表，第一個元素是頭部
        self.direction = start_dir # 初始移動方向 (x, y)
        self.score = 0 # 初始分數
        self.body_color, self.head_color = color_config # 蛇身體和頭部的顏色配置
        self.is_dead = False # 標記蛇是否死亡
        self.death_time = None # 記錄蛇死亡的時間戳 (用於多人模式平局判斷)
    def get_head_position(self):
        return self.positions[0]
    def turn(self, point):
        # 防止蛇直接掉頭 (長度大於 1 且新方向與當前方向相反)
        if self.length > 1 and (point[0] * -1, point[1] * -1) == self.direction:
            return # 不改變方向
        else:
            self.direction = point # 設定新的移動方向
    def move(self):
        # 如果蛇已死亡，不能移動
        if self.is_dead:           
            return False # 移動失敗
        cur = self.get_head_position()
        x, y = self.direction
        new_head_x = cur[0] + x
        new_head_y = cur[1] + y
        if not (0 <= new_head_x < GRID_WIDTH and 0 <= new_head_y < GRID_HEIGHT):
             return False       
        new_head = (new_head_x, new_head_y)
        if len(self.positions) > 1 and new_head in self.positions:
             # 只有當新頭部不是最後一節身體 (尾巴)，或者蛇長度小於等於 2 時才算碰撞
             if new_head != self.positions[-1] or len(self.positions) <= 2:
                 return False       
        self.positions.insert(0, new_head)
        if len(self.positions) > self.length:
            self.positions.pop()
        return True       
    def grow(self, points=1):
        # 如果蛇已死亡，不能增長
        if self.is_dead:
            return
        self.score += points # 增加分數
        self.score = max(0, self.score) # 分數不能低於 0
        if points > 0:
            # 吃加分食物，長度增加
            self.length += points          
        elif points < 0:
            # 吃扣分食物 (毒藥)，長度減少
            reduction = abs(points) 
            actual_reduction = min(reduction, self.length - 1)
            self.length -= actual_reduction
            self.length = max(1, self.length)            
            while len(self.positions) > self.length:
                 if self.positions:
                     self.positions.pop()
    def die(self):
        if not self.is_dead:               
            self.is_dead = True
            self.death_time = pygame.time.get_ticks()          
    def draw(self, surface):
        """繪製蛇，使用漸變顏色和圓角矩形效果"""
        if self.is_dead:
            pass 
        for i, p in enumerate(self.positions[::-1]):
            segment_length = len(self.positions)
            # 計算顏色漸變強度 (從 0 到約 1.2)，使得靠近頭部的顏色更接近 head_color
            gradient_intensity = min(1.0, i / max(1, segment_length - 1) * 1.2)
            base_color = self.head_color # 漸變的起始顏色 (頭部)
            target_color = self.body_color # 漸變的目標顏色 (身體)
            # 使用線性插值計算當前節點的顏色
            r = int(base_color[0] + (target_color[0] - base_color[0]) * gradient_intensity)
            g = int(base_color[1] + (target_color[1] - base_color[1]) * gradient_intensity)
            b = int(base_color[2] + (target_color[2] - base_color[2]) * gradient_intensity)
            segment_color = (r, g, b)
            rect = pygame.Rect(
                int(p[0] * GRID_SIZE), 
                int(p[1] * GRID_SIZE), 
                GRID_SIZE, GRID_SIZE
            )
            inner_rect = pygame.Rect(
                rect.x + 1, rect.y + 1, 
                rect.width - 2, rect.height - 2
            )
            # 如果蛇死亡，使用灰色；否則使用計算出的漸變色
            final_color = segment_color if not self.is_dead else (100, 100, 100)       
            pygame.draw.rect(surface, final_color, inner_rect, border_radius=min(8, GRID_SIZE // 6))
            if not self.is_dead and i == segment_length - 1:
                eye_size = max(4, GRID_SIZE // 10)
                eye_offset = GRID_SIZE // 4
                dx, dy = self.direction
                if dx == 0:
                    if dy == -1:
                        left_eye = (rect.x + eye_offset, rect.y + eye_offset)
                        right_eye = (rect.x + GRID_SIZE - eye_offset - eye_size, rect.y + eye_offset)
                    else:
                        left_eye = (rect.x + eye_offset, rect.y + GRID_SIZE - eye_offset - eye_size)
                        right_eye = (rect.x + GRID_SIZE - eye_offset - eye_size, rect.y + GRID_SIZE - eye_offset - eye_size)
                else:
                    if dx == -1:
                        left_eye = (rect.x + eye_offset, rect.y + eye_offset)
                        right_eye = (rect.x + eye_offset, rect.y + GRID_SIZE - eye_offset - eye_size)
                    else:
                        left_eye = (rect.x + GRID_SIZE - eye_offset - eye_size, rect.y + eye_offset)
                        right_eye = (rect.x + GRID_SIZE - eye_offset - eye_size, rect.y + GRID_SIZE - eye_offset - eye_size)
                pygame.draw.rect(surface, BLACK, (*left_eye, eye_size, eye_size))
                pygame.draw.rect(surface, BLACK, (*right_eye, eye_size, eye_size))

class Food:
    def __init__(self, occupied_positions, food_type_data):
        self.type = food_type_data['type']
        self.score = food_type_data['score']
        self.color = food_type_data['color']
        self.image_path = food_type_data['image']
        self.image = None
        self.use_image = False
        self.position = (0, 0)
        self.created_time = pygame.time.get_ticks()
        self.load_image()
        self.randomize_position(occupied_positions)
    def load_image(self):
        """載入食物圖片"""
        try:
            if not os.path.exists(self.image_path):
                raise FileNotFoundError(f"找不到食物圖片: {self.image_path}")
            loaded_image = pygame.image.load(self.image_path).convert_alpha()
            self.image = pygame.transform.scale(loaded_image, (GRID_SIZE, GRID_SIZE))
            self.use_image = True
        except Exception as e:
            print(f"無法載入食物圖片 {self.image_path}: {e}")
            print("將使用純色矩形替代")
            self.use_image = False
    def randomize_position(self, occupied_positions):
        """確保食物生成在有效且未被佔用的位置"""
        while True:
            new_pos = (random.randint(0, GRID_WIDTH - 1),
                       random.randint(0, GRID_HEIGHT - 1))
            if new_pos not in occupied_positions:
                self.position = new_pos
                break
        self.created_time = pygame.time.get_ticks()
    def is_timed_out(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.created_time >= FOOD_TIMEOUT:
            return True
        return False
    def draw(self, surface):
        """繪製食物，如果沒有圖片則繪製精緻的圓形食物"""
        rect = pygame.Rect(
            int(self.position[0] * GRID_SIZE),
            int(self.position[1] * GRID_SIZE),
            GRID_SIZE, GRID_SIZE
        )
        current_time = pygame.time.get_ticks()
        pulse = 0.05 * math.sin(current_time * 0.003) + 0.95                    
        if self.use_image and self.image:
            scaled_size = int(GRID_SIZE * pulse)
            offset = (GRID_SIZE - scaled_size) // 2
            scaled_image = pygame.transform.scale(self.image, (scaled_size, scaled_size))
            draw_rect = pygame.Rect(
                rect.x + offset, 
                rect.y + offset, 
                scaled_size, 
                scaled_size
            )
            surface.blit(scaled_image, draw_rect)
        else:
            center_x = rect.x + GRID_SIZE // 2
            center_y = rect.y + GRID_SIZE // 2
            radius = int((GRID_SIZE // 2 - 2) * pulse)
            pygame.draw.circle(surface, self.color, (center_x, center_y), radius)
            highlight_radius = radius // 3
            highlight_offset = highlight_radius // 2
            pygame.draw.circle(
                surface, 
                (255, 255, 255), 
                (center_x - highlight_offset, center_y - highlight_offset), 
                highlight_radius
            )
            shadow_color = (max(0, self.color[0] - 40), max(0, self.color[1] - 40), max(0, self.color[2] - 40))
            pygame.draw.circle(
                surface,
                shadow_color,
                (center_x, center_y),
                radius,
                2         
            )

class Button:
    def __init__(self, x, y, width, height, text, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.color = BUTTON_COLOR
        self.hover_color = BUTTON_HOVER_COLOR
        self.text_color = TEXT_COLOR
        self.is_hovered = False
        self.shadow_color = (0, 0, 0, 150)         
        self.border_radius = 10        
        self.shadow_offset = 4        
    def draw(self, surface):
        shadow_rect = pygame.Rect(
            self.rect.x + self.shadow_offset,
            self.rect.y + self.shadow_offset,
            self.rect.width,
            self.rect.height
        )
        shadow_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(
            shadow_surface, 
            self.shadow_color, 
            pygame.Rect(0, 0, self.rect.width, self.rect.height),
            border_radius=self.border_radius
        )
        surface.blit(shadow_surface, shadow_rect)
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(
            surface, 
            color, 
            self.rect, 
            border_radius=self.border_radius
        )
        border_color = (0, 0, 0, 255) if not self.is_hovered else (255, 255, 255, 150)
        pygame.draw.rect(
            surface, 
            border_color, 
            self.rect, 
            width=2,
            border_radius=self.border_radius
        )
        text_surface = self.font.render(self.text, False, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        if self.is_hovered:
            text_rect.y -= 2
        surface.blit(text_surface, text_rect)
        if self.is_hovered:
            current_time = pygame.time.get_ticks()
            highlight_alpha = int(100 * abs(math.sin(current_time * 0.005)))
            highlight_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            highlight_surface.fill((255, 255, 255, highlight_alpha))
            highlight_mask = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            pygame.draw.rect(
                highlight_mask, 
                (255, 255, 255, 255), 
                pygame.Rect(0, 0, self.rect.width, self.rect.height), 
                border_radius=self.border_radius
            )
            highlight_surface.blit(highlight_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            surface.blit(highlight_surface, self.rect.topleft)
    def update(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
    def check_click(self, mouse_pos, mouse_click):
        if self.rect.collidepoint(mouse_pos) and mouse_click:
            return True
        return False

class AISnake(Snake):
    def __init__(self, player_id, start_pos, start_dir, color_config):
        super().__init__(player_id, start_pos, start_dir, color_config)
        self.target_food = None          
    def decide_direction(self, foods, other_snakes):
        """簡單的 AI 決策：追蹤最近的食物，避開障礙物"""
        non_poison_foods = [f for f in foods if f.type != 'poison']
        target_foods = non_poison_foods if non_poison_foods else foods
        if not target_foods:
             return
        head = self.get_head_position()
        target_foods.sort(key=lambda f: abs(f.position[0] - head[0]) + abs(f.position[1] - head[1]))
        self.target_food = target_foods[0]
        target_pos = self.target_food.position
        obstacles = set()
        for x in range(-1, GRID_WIDTH + 1):
            obstacles.add((x, -1))
            obstacles.add((x, GRID_HEIGHT))
        for y in range(-1, GRID_HEIGHT + 1):
            obstacles.add((-1, y))
            obstacles.add((GRID_WIDTH, y))
        for snake in other_snakes:
            if snake == self:
                obstacles.update(self.positions[1:])
            else:
                 obstacles.update(snake.positions)
        possible_moves = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        current_dx, current_dy = self.direction
        reverse_direction = (-current_dx, -current_dy)
        if self.length > 1 and reverse_direction in possible_moves:
            possible_moves.remove(reverse_direction)
        possible_moves.sort(key=lambda move: (
            abs((head[0] + move[0]) - target_pos[0]) + 
            abs((head[1] + move[1]) - target_pos[1])
        ))
        best_direction = None
        for move in possible_moves:
            next_head_x = head[0] + move[0]
            next_head_y = head[1] + move[1]
            next_pos = (next_head_x, next_head_y)
            if next_pos not in obstacles:
                best_direction = move
                break 
        if best_direction is None:
             safe_moves = [m for m in [(0,-1),(0,1),(-1,0),(1,0)] if m != reverse_direction or self.length <= 1]
             random.shuffle(safe_moves)
             for move in safe_moves:
                 next_head_x = head[0] + move[0]
                 next_head_y = head[1] + move[1]
                 next_pos = (next_head_x, next_head_y)
                 if next_pos not in obstacles:
                     best_direction = move
                     break
        if best_direction is None:
            best_direction = self.direction
        self.direction = best_direction
    def move(self):
        return super().move()