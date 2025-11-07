import os
import math
import sys
import pygame as pg
import random

WIDTH, HEIGHT = 900, 600
FPS = 60
os.chdir(os.path.dirname(os.path.abspath(__file__)))

BG = (135, 206, 235)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BROWN = (139, 69, 19)
GOLD = (255, 215, 0)
GROUND = (220, 235, 237)
FLOATING_ICE = (53, 94, 144)
PLAYER_COLOR = (220, 20, 60)

ground_y = HEIGHT - 50 
stage_index = 0



class Player:
    def __init__(self, x, y):
        self.rect = pg.Rect(x, y, 40, 50)
        self.vx = 0
        self.vy = 0
        # 追加機能1(近藤): パワーアップ機能の状態を保持
        self.base_speed = 5
        self.base_jump_power = 14
        self.jump_enabled = True
        # パワーアップ状態
        self.power = None  # 'fire','ice','jump','suberu','muteki'
        self.power_time = 0.0
        # 衝突後の短い無敵フレーム（秒）
        self.invul_time = 0.0
        # 向きフラグ: 1 = 右, -1 = 左
        # 追加機能3(近藤): 向き（弾発射時に使用）
        self.facing = 1
        self.on_ground = False
        self.color = PLAYER_COLOR
        self.color_timer = 0  # 色保持用タイマー（フレーム数）
        self.jump_power = self.base_jump_power
        self.speed = self.base_speed

    def handle_input(self, keys):
        self.vx = 0
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            self.vx = -self.speed
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.vx = self.speed
        # 移動時に向きを更新する
        if self.vx > 0:
            self.facing = 1
        elif self.vx < 0:
            self.facing = -1
        if (keys[pg.K_SPACE] or keys[pg.K_z] or keys[pg.K_UP]) and self.on_ground and self.jump_enabled:
            self.vy = -self.jump_power
            self.on_ground = False

    def apply_gravity(self):
        self.vy += 0.8  # 重力
        if self.vy > 20:
            self.vy = 20

    def update(self, platforms, blocks=None, items=None):
        # 水平移動
        self.rect.x += int(self.vx)
        self._collide(self.vx, 0, platforms)
        # vertical movement
        self.apply_gravity()
        self.rect.y += int(self.vy)
        self.on_ground = False
        self._collide(0, self.vy, platforms)

        # 画面左に進めないようにする
        if self.rect.left < 0:
            self.rect.left = 0
            self.vx = 0

        # はてなブロックを下から叩く
        for b in blocks[:]:
            if self.rect.colliderect(b.rect):
                if self.vy < 0 and self.rect.top <= b.rect.bottom:
                    self.rect.top = b.rect.bottom
                    self.vy = 0
                    b.activate(items)
                    blocks.remove(b)
        
        # アイテム取得（パワーアップ）
        for i in items[:]:
            if self.rect.colliderect(i.rect):
                self.color = i.color
                self.color_timer = FPS * 5  # 5秒間色を保持

        # 色タイマー処理
        if self.color_timer > 0:
            self.color_timer -= 1
        elif self.color_timer == 0:
            self.color = PLAYER_COLOR
    
    def update_power(self, dt):
        if self.power is not None:
            self.power_time -= dt
            if self.power_time <= 0:
                self.clear_power()

    def _collide(self, vx, vy, platforms):
        for p in platforms:
            if self.rect.colliderect(p):
                if vx > 0:  # 右
                    self.rect.right = p.left
                if vx < 0:  # 左
                    self.rect.left = p.right
                if vy > 0:  # 落下
                    self.rect.bottom = p.top
                    self.vy = 0
                    self.on_ground = True
                if vy < 0:  # ジャンプ
                    self.rect.top = p.bottom
                    self.vy = 0

    def draw(self, surf):
        # パワーアップに応じてキャラクターの色が変わる
        if self.power == 'muteki':
            # レインボー
            t = pg.time.get_ticks() / 100.0
            r = int((1 + math.sin(t)) * 127) % 256
            g = int((1 + math.sin(t + 2)) * 127) % 256
            b = int((1 + math.sin(t + 4)) * 127) % 256
            self.color = (r, g, b)
        elif self.power == 'fire':
            self.color = (255, 140, 0)  # オレンジ（火）
        elif self.power == 'ice':
            self.color = (100, 200, 255)  # 水色（氷）
        elif self.power == 'jump':
            self.color = (255, 215, 0)  # ゴールド
        elif self.power == 'suberu':
            self.color = (160, 160, 160)  # グレー
        # else:
        #     self.color = RED
        pg.draw.rect(surf, self.color, self.rect)


# class Enemy:
#     def __init__(self, x, y, w=100, h=100, left_bound=None, right_bound=None):
#         self.image = pg.image.load("sirokuma.png").convert_alpha()  # 白熊画像を読み込む
#         self.image = pg.transform.scale(self.image, (w, h))         # 画像サイズ調整
#         self.rect = self.image.get_rect(topleft=(x, y))             # rectを画像から取得
#         self.vx = 1.1  # 移動速度
#         self.left_bound = left_bound
#         self.right_bound = right_bound

#         # 出現位置：右端から
#         if x is None:
#             x = right_bound
#         self.rect = self.image.get_rect(topleft=(x, y))

#         # 左方向に移動スタート
#         self.vx = -3  

#         # 移動範囲
#         self.left_bound = left_bound
#         self.right_bound = right_bound
#     def apply_power(self, power: str, duration: float = 8.0):
#         """
#         プレイヤーに数秒間パワーアップを適用します。
#         power: 'fire','ice','jump','suberu','muteki'
#         """
#         # 以前のクラスをリセットする
#         self.speed = self.base_speed
#         self.jump_power = self.base_jump_power
#         self.jump_enabled = True
#         self.can_kill_on_touch = False

#         self.power = power
#         self.power_time = float(duration)
        
#         if power == 'fire' or power == 'ice':
#             self.can_kill_on_touch = True
#         elif power == 'jump':
#             self.jump_power = self.base_jump_power * 2
#         elif power == 'suberu':
#             self.speed = int(self.base_speed * 1.6)
#             self.jump_enabled = False
#         elif power == 'muteki':
#             # muteki: 敵の衝突を無視（無敵状態）
#             pass


    def update_power(self, dt: float):
        """
        時間切れが来たら元の状態に戻る
        """
        # パワー時間の減少
        if self.power_time > 0:
            self.power_time -= dt
            if self.power_time <= 0:
                # 時間切れで元に戻す
                self.power = None
                self.power_time = 0.0
                self.speed = self.base_speed
                self.jump_power = self.base_jump_power
                self.jump_enabled = True
                self.can_kill_on_touch = False
                self.clear_power()
        # 無敵時間の減少
        if self.invul_time > 0:
            self.invul_time -= dt
            if self.invul_time < 0:
                self.invul_time = 0.0

    def clear_power(self):
        """能力が切れたら、基本ステータスに戻す"""
        self.power = None
        self.power_time = 0.0
        self.speed = self.base_speed
        self.jump_power = self.base_jump_power
        self.jump_enabled = True
        self.can_kill_on_touch = False

# ハテナブロック
class hatena:
    def __init__(self, x, y):
        self.rect = pg.Rect(x, y, 40, 40)
        self.used = False

    def activate(self, items):
        if not self.used:
            self.used = True
            kind = random.choice(["fire", "ice", "jump", "suberu", "muteki"])
            item = Item(self.rect.x + 12, self.rect.y - 20, kind)
            items.append(item)

    def draw(self, surf):
        color = (192,192,192) if self.used else (255,255,0)
        pg.draw.rect(surf, color, self.rect)
        if not self.used:
            pg.draw.rect(surf, BLACK, self.rect, 2)
            font = pg.font.Font(None, 30)
            q = font.render("?", True, BLACK)
            surf.blit(q, (self.rect.x + 13, self.rect.y + 7))

#アイテム
class Item:
    color_dict = {
        'fire': (255, 100, 0),
        'ice': (100, 200, 255),
        'jump': (255, 215, 0),
        'suberu': (160, 160, 160),
        'muteki': (255, 0, 255),
    }

    def __init__(self, x, y, kind: str, w=16, h=16, duration: float = 8.0):
        self.rect = pg.Rect(x, y, w, h)
        self.kind = kind  # 'fire','ice','jump','suberu','muteki'
        self.color = self.color_dict.get(kind, (255, 215, 0))
        self.vy = -4
        self.rise_frames = 20
        self.stop_y = y - 10
        self.duration = duration

    def update(self):
        if self.rise_frames > 0:
            self.rect.y += self.vy
            self.rise_frames -= 1
            if self.rise_frames == 0:
                self.rect.y = self.stop_y

    def draw(self, surf):
        pg.draw.rect(surf, self.color, self.rect)


class Enemy:
    def __init__(self, x, y, w=40, h=40, left_bound=None, right_bound=None, falling=False):
        self.rect = pg.Rect(x, y, w, h)
        self.vx = 2 if not falling else 0
        self.vy = 0
        self.left_bound = left_bound
        self.right_bound = right_bound
        self.falling = falling
        self.image = pg.Surface((w,h))
        self.image.fill((255,0,0))  # 赤色の敵

    def update(self, platforms, screen_width=None):
        # 落下中
        if self.falling:
            self.vy += 0.8
            if self.vy > 20:
                self.vy = 20
            self.rect.y += int(self.vy)
            # 地面との衝突判定
            for p in platforms:
                if self.rect.colliderect(p) and self.rect.bottom - self.vy <= p.top + 5:
                    self.rect.bottom = p.top
                    self.vy = 0
                    self.falling = False
                    self.vx = 2
                    break
            return  # ← 落下中は横移動しない

        self.rect.x += int(self.vx)  # 敵が徘徊するようにする
        # 左限界チェック
        if self.left_bound is not None and self.rect.left < self.left_bound:
            self.rect.left = self.left_bound
            self.vx *= -1
        # 右限界チェック
        if self.right_bound is not None and self.rect.right > self.right_bound:
            self.rect.right = self.right_bound
            self.vx *= -1
        # 画面外制限
        if self.rect.left < 0:
            self.rect.left = 0
            self.vx *= -1
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
            self.vx *= -1

    def draw(self, surf):
        surf.blit(self.image, self.rect)


# 落ちてくる敵
class FallingEnemy:
    def __init__(self, x, y, w=40, h=40, speed=2):
        self.rect = pg.Rect(x, y, w, h)
        self.vy = speed  # 落下速度

    def update(self): 
        self.rect.y += self.vy  # 下に落ちる

        # 画面外に出たら上にリセット
        if self.rect.top > HEIGHT:
            self.rect.bottom = 0

    def draw(self, surf):
        pg.draw.rect(surf, (0, 0, 255), self.rect)  # 青色の敵



# ゴールクラス
class Goal(pg.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pg.Surface((60, 60))
        self.image.fill(GOLD)
        self.rect = self.image.get_rect(topleft=(x, y))


def build_level():
    platforms = []
    platforms.append(pg.Rect(0, HEIGHT - 40, WIDTH, 40))
    platforms.append(pg.Rect(100, 460, 200, 20))
    platforms.append(pg.Rect(380, 360, 180, 20))
    platforms.append(pg.Rect(600, 280, 220, 20))
    platforms.append(pg.Rect(250, 520, 120, 20))
    platforms.append(pg.Rect(480, 520, 80, 20))
    return platforms

def build_stage1():
    """
    1つ目のステージを生成する関数
    戻り値：地面・浮島・はてなブロック・敵のリスト(以下build関数は同文)
    """
    ground_platforms = [
        pg.Rect(0, ground_y, 200, 40),
        pg.Rect(250, ground_y, 50, 40),
        pg.Rect(350, ground_y, 50, 40),
        pg.Rect(500, ground_y, 50, 40),
        pg.Rect(600, ground_y, 50, 40),
        pg.Rect(700, ground_y, WIDTH, 40)
    ]
    floating_platforms = [
        pg.Rect(100, 500, 50, 50),
        pg.Rect(250, 400, 150, 50)
    ]
    hatena_platforms = [pg.Rect(350, 300, 50, 50)]
    enemies = [Enemy(700, ground_y - 40, left_bound=700)]
    return ground_platforms, floating_platforms, hatena_platforms, enemies

def build_stage2():
    """2つ目のステージを生成する関数"""
    ground_platforms = [
        pg.Rect(0, ground_y, 550, 40),
        pg.Rect(650, ground_y, 150, 40)
    ]
    floating_platforms = [
        pg.Rect(200, 500, 50, 50),
        pg.Rect(300, 400, 50, 50),
        pg.Rect(400, 300, 50, 50),
        pg.Rect(500, 200, 50, 50),
        pg.Rect(650, 350, 50, 50),
        pg.Rect(800, 350, 100, 50)
    ]
    hatena_platforms = []
    enemies = []
    return ground_platforms, floating_platforms, hatena_platforms, enemies

def build_stage3():
    """3つ目のステージを生成する関数"""
    ground_platforms = [pg.Rect(0, ground_y, WIDTH, 40)]
    floating_platforms = [
        pg.Rect(0, 200, 250, 50),
        pg.Rect(300, 350, 200, 50),
        pg.Rect(600, 450, 250, 50)
    ]
    hatena_platforms = [
        pg.Rect(50, 100,
                 50, 50),
        pg.Rect(700, 350, 50, 50)
    ]
    enemies = [Enemy(200, 510), Enemy(300, 0, falling=True, left_bound=300, right_bound=500)]
    return ground_platforms, floating_platforms, hatena_platforms, enemies

def build_stage4():
    """4つ目のステージを生成する関数"""
    hatena_platforms = []
    ground_platforms = [pg.Rect(0, ground_y, WIDTH, 40)]
    floating_platforms = [
        pg.Rect(100, ground_y-50, 50, 50),
        pg.Rect(200, 400, 100, 50),
        pg.Rect(350, 300, 50, 50),
        pg.Rect(450, 200, 100, 50),
        pg.Rect(600, 100, 50, 50),
        pg.Rect(700, 200, 50, 50),
        pg.Rect(800, 100, 50, 50)
    ]
    enemies = [Enemy(400, ground_y - 40), Enemy(650, ground_y - 40)]
    return ground_platforms, floating_platforms, hatena_platforms, enemies

def build_stage5():
    """5つ目のステージを生成する関数"""
    ground_platforms = [pg.Rect(0, ground_y, WIDTH, 40)]
    floating_platforms = [
        pg.Rect(150, 500, 50, 50),
        pg.Rect(200, 450, 50, 50),
        pg.Rect(250, 400, 50, 150),
        pg.Rect(750, 450, 50, 100),
        pg.Rect(800, 450, 100, 50),
        pg.Rect(400, 300, 150, 50),
        pg.Rect(650, 200, 250, 50)
    ]
    hatena_platforms = [pg.Rect(750, 90, 50, 50)]
    enemies = [Enemy(350, ground_y - 40, left_bound=300, right_bound=750),
               Enemy(450, ground_y - 40, left_bound=300, right_bound=750),
               Enemy(550, ground_y - 40, left_bound=300, right_bound=750),
               Enemy(650, ground_y - 40, left_bound=300, right_bound=750)]
    return ground_platforms, floating_platforms, hatena_platforms, enemies

def build_stage6():
    """6つ目のステージを生成する関数"""
    ground_platforms = [pg.Rect(0, ground_y, WIDTH, 40)]
    floating_platforms = [
        pg.Rect(0, 500, 50, 50),
        pg.Rect(350, 500, 200, 50),
        pg.Rect(300, 300, 250, 50),
        pg.Rect(650, 400, 50, 50),
        pg.Rect(700, 450, 200, 50)
    ]
    hatena_platforms = [pg.Rect(400, 190, 50, 50)]
    enemies = [Enemy(200, 0, falling=True, left_bound=50, right_bound=350)]
    return ground_platforms, floating_platforms, hatena_platforms, enemies

def build_stage7():
    """7つ目のステージを生成する関数"""
    ground_platforms = [
        pg.Rect(0, ground_y, 250, 40),
        pg.Rect(350, ground_y, 350, 40),
        pg.Rect(800, ground_y, 100, 40)
    ]
    floating_platforms = []
    hatena_platforms = [pg.Rect(150, 440, 50, 50)]
    enemies = [Enemy(500, 0, falling=True,left_bound=350, right_bound=700)]
    return ground_platforms, floating_platforms, hatena_platforms, enemies

def build_stage8():
    """8つ目のステージを生成する関数"""
    ground_platforms = [pg.Rect(0, ground_y, WIDTH, 40)]
    floating_platforms = [
        pg.Rect(150, 500, 50, 50),
        pg.Rect(200, 400, 250, 50),
        pg.Rect(750, 500, 50, 50),
        pg.Rect(500, 400, 250, 50)
    ]
    hatena_platforms = [pg.Rect(WIDTH/2, 290, 50, 50)]
    enemies = [Enemy(700, ground_y - 40, left_bound=200, right_bound=750), 
               Enemy(200, 0,falling=True, left_bound=200, right_bound=450)]
    return ground_platforms, floating_platforms, hatena_platforms, enemies

def build_stage9():
    """9つ目のステージを生成する関数"""
    ground_platforms = [pg.Rect(0, ground_y, WIDTH, 40)]
    floating_platforms = [pg.Rect(150, 450, 150, 50),pg.Rect(300, 350, 150, 50), pg.Rect(400, 250, 150, 50),pg.Rect(500, 350, 150, 50),pg.Rect(650, 450, 150, 50)]
    hatena_platforms = []
    enemies = [Enemy(300, ground_y - 40)]
    return ground_platforms, floating_platforms, hatena_platforms, enemies

def build_stage10():
    """10つ目のステージを生成する関数"""
    ground_platforms = [pg.Rect(0, ground_y, 550, 40),pg.Rect(650, ground_y, 250, 40)]
    floating_platforms = [pg.Rect(150, 500, 400, 50),pg.Rect(250, 450, 300, 50),pg.Rect(350, 400, 200, 50),pg.Rect(450, 350, 100, 50),pg.Rect(650, 350, 250, 200),pg.Rect(700, 300, 200, 50)]
    hatena_platforms = []
    enemies = [Enemy(750, 0, falling=True, left_bound=700)]
    return ground_platforms, floating_platforms, hatena_platforms, enemies

def build_goal():
    """
    ゴールステージ画面を生成する関数。旗に触れるとゴールする。
    戻り値：ステージ名、地面のリスト、ゴールのリスト(中身は１つだけ)
    """
    ground_platforms = [pg.Rect(0, ground_y, WIDTH, 50)]
    goal_platforms = [Goal(WIDTH - 80, ground_y - 80)]
    return ground_platforms, goal_platforms


class Projectile:
    """プレイヤーが火/氷の力を持っているときに発射する弾"""
    def __init__(self, x, y, kind: str, direction: int, speed: float = 10.0):
        self.rect = pg.Rect(int(x), int(y), 10, 10)
        self.kind = kind
        self.vx = speed * (1 if direction >= 0 else -1)

    def update(self):
        self.rect.x += int(self.vx)

    def draw(self, surf):
        color = (255, 100, 0) if self.kind == 'fire' else (100, 200, 255)
        pg.draw.rect(surf, color, self.rect)

# コメントアウトした
# class Goal:
#     def __init__(self, x, y, w=40, h=80):
#         self.rect = pg.Rect(x, y, w, h)

#     def draw(self, surf):
#         pg.draw.rect(surf, (0, 200, 0), self.rect)


# STAGE_BUILDERS = [build_stage1,build_stage2,build_stage3,build_stage4,build_stage5,build_stage6,build_stage7,build_stage8,build_stage9,build_stage10]
# STAGE_BUILDERS = [build_stage1]

STAGE_BUILDERS = [build_stage4]  # デバッグ用　　　　　　
# ステージ3,4,7,9がクリアしやすいかも



def draw_text(surf, text, size, x, y, color=BLACK, center=True):
    font = pg.font.Font(None, size)
    txt = font.render(text, True, color)
    rect = txt.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    surf.blit(txt, rect)


def main():
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption("北極探検ゲーム")
    clock = pg.time.Clock()
    # pg.display.set_caption("Hatena")
    # clock = pg.time.Clock()

    # コメントアウトした
    # player = Player(50, HEIGHT - 90)

    global stage_index
    goal_platforms = []
    # 最初のステージを作る
    if(stage_index == 0):
        ground_platforms, floating_platforms, hatena_platforms, enemies = random.choice(STAGE_BUILDERS)()
    platforms = ground_platforms + floating_platforms
    # 追加しました
    # falling_enemies = [FallingEnemy(200, 0, speed=2), FallingEnemy(500, -150, speed=2)]
    # goal = Goal(700, 100)

    font = pg.font.Font(None, 36)
    score = 0
    items = []  # レベルに配置するパワーアップアイテム
    projectiles = []   # 球発射
    # 
    # blocks = [hatena(r.x, r.y) for r in hatena_platforms]

# もともと
    # # 初期化
    # def init_game():
    #     player = Player(50, HEIGHT - 90 - 50)
    #     # 初期ステージを構築
    #     platforms = build_stage1()
    #     # coins = []
    #     enemies = [Enemy(x=WIDTH - 200, y=HEIGHT - 140, w=120, h=120, left_bound=0, right_bound=WIDTH - 120)]
    #     falling_enemies = [FallingEnemy(200, 0, speed=2), FallingEnemy(500, -150, speed=2)]
    #     goal = Goal(700, 100)
        
    #     # score = 0
    #     # return player, platforms, coins, enemies, falling_enemies, goal, score
    #     return player, platforms, enemies, falling_enemies, goal
    
        # 初期化
    def init_game():
        player = Player(50, HEIGHT - 90 - 50)
        falling_enemies = [FallingEnemy(200, 0, speed=2), FallingEnemy(500, -150, speed=2)]
        goal = Goal(700, 100)
        # 初期ステージを構築
        ground_platforms, floating_platforms, hatena_platforms, enemies = build_stage1()
        platforms = ground_platforms + floating_platforms
    
        return player, platforms, enemies, falling_enemies, goal, hatena_platforms, ground_platforms, floating_platforms


    # # player, platforms, coins, enemies, falling_enemies, goal, score = init_game()
    player, platforms, enemies, falling_enemies, goal, hatena_platforms, ground_platforms, floating_platforms = init_game()

    # 移設
    blocks = [hatena(r.x, r.y) for r in hatena_platforms]

    state = "start"
    goal_visible = True  # 最初から表示

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.KEYDOWN and event.key == pg.K_x:
                # プレイヤーが火または氷の力を持っている場合にのみ発射物を生成します
                if player.power in ('fire', 'ice'):
                    px = player.rect.centerx + player.facing * (player.rect.width//2 + 5)
                    py = player.rect.centery
                    projectiles.append(Projectile(px, py, player.power, player.facing))

        keys = pg.key.get_pressed()

        # keys = pg.key.get_pressed()

        # スタート画面
        if state == "start":
            screen.fill(BG)
            draw_text(screen, "GAME START", 80, WIDTH // 2, HEIGHT // 3, WHITE)
            draw_text(screen, "Press SPACE to Start", 40, WIDTH // 2, HEIGHT // 2)
            draw_text(screen, "< >: Move    SPACE : Jump", 30, WIDTH // 2, HEIGHT // 2 + 60, BLACK)
            pg.display.flip()
            if keys[pg.K_SPACE]:
                state = "play"
            continue

        # ゲームプレイ中
        if state == "play":
            player.handle_input(keys)
            player.update(platforms,blocks,items)
            player.update_power(dt)

            for e in enemies:
                e.update(platforms)
            for fe in falling_enemies:
                fe.update()
                fe.draw(screen)
            
                    # # 発射物を更新する
            for p in projectiles[:]:
                p.update()
                # 画面外の場合は削除
                if p.rect.right < 0 or p.rect.left > WIDTH:
                    # try:
                        projectiles.remove(p)
                    # except ValueError:
                    #     pass
                else:
                    # 発射物と敵の衝突
                    for e in enemies[:]:
                        if p.rect.colliderect(e.rect):
                            # try:
                                enemies.remove(e)
                            # except ValueError:
                            #     pass
                            # try:
                                projectiles.remove(p)
                            # except ValueError:
                                score += 5
                                # pass
                                break

            # アイテム取得
            for it in items[:]:
                if player.rect.colliderect(it.rect):
                    player.apply_power(it.kind, duration=it.duration)
                    items.remove(it)

        # コインの取得
        # for c in coins[:]:
        #     if player.rect.colliderect(c):
        #         coins.remove(c)
        #         score += 1

            # 敵との衝突
            dead = False
            for e in enemies[:]:
                if player.rect.colliderect(e.rect):
                    # 無敵（muteki）は触れると敵を倒す
                    if player.power == 'muteki':
                        # try:
                            enemies.remove(e)
                        # except ValueError:
                        #     pass
                            player.vy = -8
                        # continue
                    # 敵を倒すのは踏みつけ（プレイヤーが下向きに当たったとき）のみ
                    elif player.vy > 0 and player.rect.bottom <= e.rect.top + 10:
                        # try:
                            enemies.remove(e)
                        # except ValueError:
                            # pass
                            player.vy = -8
                    # else:
                        # 火/氷のパワーを持っている場合、触れても敵は倒さずパワーだけ消える。
                        # プレイヤーはその場に留まる（死なない、跳ね返らない）
                    elif player.power in ('fire', 'ice'):
                            player.clear_power()
                    else:
                        dead = True

            # コイン取得でスコア加算
            # for c in coins[:]:
            #     if player.rect.colliderect(c):
            #         coins.remove(c)
            #         score += 1


            # 敵・落下物との衝突判定
            # dead = False
            # for e in enemies:
            #     player_x_start, player_y_start = player.rect.left, player.rect.top
            #     player_x_end, player_y_end = player.rect.right, player.rect.bottom
            #     enemy_x_start, enemy_y_start = e.rect.left, e.rect.top
            #     enemy_x_end, enemy_y_end = e.rect.right, e.rect.bottom
            #     if (player_x_end > enemy_x_start and
            #         player_x_start < enemy_x_end and
            #         player_y_end > enemy_y_start and
            #         player_y_start < enemy_y_end):
            #         dead = True

            for fe in falling_enemies:
                if player.rect.colliderect(fe.rect):
                    dead = True

                # player_x_start, player_y_start = player.rect.left, player.rect.top
                # player_x_end, player_y_end = player.rect.right, player.rect.bottom
                # fe_x_start, fe_y_start = fe.rect.left, fe.rect.top
                # fe_x_end, fe_y_end = fe.rect.right, fe.rect.bottom
                # if (player_x_end > fe_x_start and
                #     player_x_start < fe_x_end and
                #     player_y_end > fe_y_start and
                #     player_y_start < fe_y_end):
                    # dead = True

            if player.rect.top > HEIGHT:
                dead = True

            if dead:
                state = "gameover"

            # ゴールとの当たり判定
            if goal_visible and player.rect.colliderect(goal.rect):
                goal_x_start, goal_y_start = goal.rect.left, goal.rect.top
                goal_x_end, goal_y_end = goal.rect.right, goal.rect.bottom
                player_x_start, player_y_start = player.rect.left, player.rect.top
                player_x_end, player_y_end = player.rect.right, player.rect.bottom

                if (player_x_start < goal_x_end and
                    player_x_end > goal_x_start and
                    player_y_start < goal_y_end and
                    player_y_end > goal_y_start):
                    state = "goal"

            # コメントアウトした
            # 描画
            # screen.fill(BG)
            # for p in platforms:
            #     pg.draw.rect(screen, BROWN, p)
            # for c in coins:
            #     pg.draw.rect(screen, GOLD, c)
            # for e in enemies:
            #     e.draw(screen)
            # for fe in falling_enemies:
            #     fe.draw(screen)
            # for it in items:
            #     it.draw(screen)
            # for proj in projectiles:
            #     proj.draw(screen)
            # player.draw(screen)

            if goal_visible:
                screen.blit(goal.image, goal.rect)

            # txt = font.render(f'Score: {score}', True, BLACK)
            # screen.blit(txt, (10, 10))
            pg.display.flip()

        # ゲームオーバー画面
        elif state == "gameover":
            screen.fill(BG)
            draw_text(screen, "GAME OVER", 80, WIDTH // 2, HEIGHT // 3, WHITE)
            # draw_text(screen, f"Your Score: {score}", 40, WIDTH // 2, HEIGHT // 2)
            draw_text(screen, "Press R to Retry or ESC to Quit", 30, WIDTH // 2, HEIGHT // 2 + 60, BLACK)
            pg.display.flip()
            if keys[pg.K_r]:
                # player, platforms, coins, enemies, falling_enemies, goal, score = init_game()
                # player, platforms, enemies, falling_enemies, goal = init_game()
                player, platforms, enemies, falling_enemies, goal, hatena_platforms, ground_platforms, floating_platforms = init_game()
                goal_visible = True  # リセット時に表示
                state = "start"
            elif keys[pg.K_ESCAPE]:
                running = False


        # ゴール画面
        elif state == "goal":
            screen.fill(BG)
            draw_text(screen, "GOAL!! Congratulations!", 70, WIDTH // 2, HEIGHT // 3, WHITE)
            # draw_text(screen, f"Score: {score}", 50, WIDTH // 2, HEIGHT // 2, BLACK)
            draw_text(screen, "Press R to Play Again or ESC to Quit", 30, WIDTH // 2, HEIGHT // 2 + 60, BLACK)
            pg.display.flip()
            if keys[pg.K_r]:
                # player, platforms, coins, enemies, falling_enemies, goal, score = init_game()
                # player, platforms, enemies, falling_enemies, goal = init_game()
                player, platforms, enemies, falling_enemies, goal, hatena_platforms, ground_platforms, floating_platforms = init_game()
                goal_visible = False
                state = "start"
            elif keys[pg.K_ESCAPE]:
                running = False
            if event.type == pg.KEYDOWN and event.key == pg.K_x:
                # プレイヤーが火または氷の力を持っている場合にのみ発射物を生成します
                if player.power in ('fire', 'ice'):
                    px = player.rect.centerx + player.facing * (player.rect.width//2 + 5)
                    py = player.rect.centery
                    projectiles.append(Projectile(px, py, player.power, player.facing))

        keys = pg.key.get_pressed()
        player.handle_input(keys)
        player.update(platforms, blocks, items)

        # パワーアップタイマーを更新する
        player.update_power(dt)
        for e in enemies:
            e.update(platforms)

        for it in items[:]:
            it.update()

        # 発射物を更新する
        for p in projectiles[:]:
            p.update()
            # 画面外の場合は削除
            if p.rect.right < 0 or p.rect.left > WIDTH:
                try:
                    projectiles.remove(p)
                except ValueError:
                    pass
            else:
                # 発射物と敵の衝突
                for e in enemies[:]:
                    if p.rect.colliderect(e.rect):
                        try:
                            enemies.remove(e)
                        except ValueError:
                            pass
                        try:
                            projectiles.remove(p)
                        except ValueError:
                            # score += 5
                            pass
                        break

        # アイテム取得
        for it in items[:]:
            if player.rect.colliderect(it.rect):
                player.apply_power(it.kind, duration=it.duration)
                items.remove(it)

        # コインの取得
        # for c in coins[:]:
        #     if player.rect.colliderect(c):
        #         coins.remove(c)
        #         score += 1

        # 敵との衝突
        dead = False
        for e in enemies[:]:
            if player.rect.colliderect(e.rect):
                # 無敵（muteki）は触れると敵を倒す
                if player.power == 'muteki':
                    try:
                        enemies.remove(e)
                    except ValueError:
                        pass
                    player.vy = -8
                    continue
                # 敵を倒すのは踏みつけ（プレイヤーが下向きに当たったとき）のみ
                if player.vy > 0 and player.rect.bottom <= e.rect.top + 10:
                    try:
                        enemies.remove(e)
                    except ValueError:
                        pass
                    player.vy = -8
                else:
                    # 火/氷のパワーを持っている場合、触れても敵は倒さずパワーだけ消える。
                    # プレイヤーはその場に留まる（死なない、跳ね返らない）
                    if player.power in ('fire', 'ice'):
                        player.clear_power()
                    else:
                        dead = True

        # ゴール判定
        # 今はゲームが終わるようになっている
        for g in goal_platforms:
            if player.rect.colliderect(g.rect):
                print("Goal")
                running = False

        # 穴に落ちたら死亡
        if player.rect.top > HEIGHT:
            dead = True

        # 死亡処理
        if dead:
            print("dead")
            running = False
            break

        # ステージ切り替え
        if player.rect.right > WIDTH:
            stage_index += 1
            if stage_index == 2:
                # ゴール
                ground_platforms, goal_platforms = build_goal()
                floating_platforms = []
                hatena_platforms = []
                enemies = []
                platforms = ground_platforms
            else:
                # 次のステージ
                ground_platforms, floating_platforms, hatena_platforms, enemies = random.choice(STAGE_BUILDERS)()
                blocks = [hatena(r.x, r.y) for r in hatena_platforms]
                platforms = ground_platforms + floating_platforms + hatena_platforms
                goal_platforms = []
            # プレイヤーを左端に戻す
            player.rect.left = 0

        # 描画
        screen.fill(BG)

        # 描画(地面・浮島・はてなブロック・ゴール)
        for p in ground_platforms:
            pg.draw.rect(screen, GROUND, p)
        for p in floating_platforms:
            pg.draw.rect(screen, FLOATING_ICE, p)
        for b in blocks:
            b.draw(screen)
        for e in enemies:
            e.draw(screen)
        for g in goal_platforms:
            g.draw(screen)
        for it in items:
            it.draw(screen)
        for proj in projectiles:
            proj.draw(screen)

        player.draw(screen)
        pg.display.flip()

    pg.quit()


if __name__ == '__main__':
    main()

