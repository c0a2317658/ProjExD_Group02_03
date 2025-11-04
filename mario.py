import os
import pygame as pg
import random


WIDTH, HEIGHT = 900, 600
FPS = 60
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Colors
BG = (135, 206, 235)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (50, 205, 50)
BROWN = (139, 69, 19)
YELLOW = (255, 255, 0)
SILVER = (192, 192, 192)
FLAG_COLOR = (0, 0, 0)
PLAYER_DEFAULT_COLOR = (220, 20, 60)  # 赤


class Player:
    def __init__(self, x, y):
        self.rect = pg.Rect(x, y, 40, 50)
        self.vx = 0
        self.vy = 0
        self.speed = 5
        self.jump_power = 14
        self.on_ground = False
        self.color = PLAYER_DEFAULT_COLOR
        self.color_timer = 0  # 色保持用タイマー（フレーム数）

    def handle_input(self, keys):
        self.vx = 0
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            self.vx = -self.speed
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.vx = self.speed
        if (keys[pg.K_SPACE] or keys[pg.K_z] or keys[pg.K_UP]) and self.on_ground:
            self.vy = -self.jump_power
            self.on_ground = False

    def apply_gravity(self):
        self.vy += 0.8
        if self.vy > 20:
            self.vy = 20

    def update(self, platforms, blocks, items):
        # horizontal movement
        self.rect.x += int(self.vx)
        self.collide(self.vx, 0, platforms)
        # vertical movement
        self.apply_gravity()
        self.rect.y += int(self.vy)
        self.on_ground = False
        self.collide(0, self.vy, platforms)

        # ブロックを下から叩く
        for b in blocks:
            if self.rect.colliderect(b.rect):
                if self.vy < 0 and self.rect.top < b.rect.bottom:
                    self.rect.top = b.rect.bottom
                    self.vy = 0
                    b.activate(items)

        # アイテム取得
        for i in items[:]:
            if self.rect.colliderect(i.rect):
                self.color = i.color
                self.color_timer = FPS * 5  # 5秒間色を保持
                items.remove(i)

        # 色タイマー処理
        if self.color_timer > 0:
            self.color_timer -= 1
        elif self.color_timer == 0:
            self.color = PLAYER_DEFAULT_COLOR

    def collide(self, vx, vy, platforms):
        for p in platforms:
            if self.rect.colliderect(p):
                if vx > 0:
                    self.rect.right = p.left
                if vx < 0:
                    self.rect.left = p.right
                if vy > 0:
                    self.rect.bottom = p.top
                    self.vy = 0
                    self.on_ground = True
                if vy < 0:
                    self.rect.top = p.bottom
                    self.vy = 0

    def draw(self, surf):
        pg.draw.rect(surf, self.color, self.rect)

# ハテナブロック
class hatena:
    def __init__(self, x, y):
        self.rect = pg.Rect(x, y, 40, 40)
        self.used = False

    def activate(self, items):
        if not self.used:
            self.used = True
            kind = random.choice(["fire", "ice", "jump", "slippery", "invincible"])
            item = Item(self.rect.x + 10, self.rect.y - 25, kind)
            items.append(item)

    def draw(self, surf):
        color = SILVER if self.used else YELLOW
        pg.draw.rect(surf, color, self.rect)
        if not self.used:
            pg.draw.rect(surf, BLACK, self.rect, 2)
            font = pg.font.Font(None, 30)
            q = font.render("?", True, BLACK)
            surf.blit(q, (self.rect.x + 13, self.rect.y + 13))

#アイテム
class Item:
    color_dict = {
        "fire": (255, 120, 0),
        "ice": (150, 220, 255),
        "jump": (0, 200, 255),
        "slippery": (180, 180, 255),
        "invincible": (255, 255, 255)
    }

    def __init__(self, x, y, kind):
        self.rect = pg.Rect(x, y, 20, 20)
        self.kind = kind
        self.color = self.color_dict.get(kind, (255, 215, 0))
        self.vy = -4
        self.rise_frames = 20
        self.stop_y = y - 10

    def update(self):
        if self.rise_frames > 0:
            self.rect.y += self.vy
            self.rise_frames -= 1
            if self.rise_frames == 0:
                self.rect.y = self.stop_y

    def draw(self, surf):
        pg.draw.rect(surf, self.color, self.rect)
        pg.draw.rect(surf, BLACK, self.rect, 1)


class Enemy:
    def __init__(self, x, y, w=40, h=40, left_bound=None, right_bound=None):
        self.rect = pg.Rect(x, y, w, h)
        self.vx = 2
        self.left_bound = left_bound
        self.right_bound = right_bound

    def update(self):
        self.rect.x += self.vx
        if self.left_bound and self.rect.left < self.left_bound:
            self.rect.left = self.left_bound
            self.vx *= -1
        if self.right_bound and self.rect.right > self.right_bound:
            self.rect.right = self.right_bound
            self.vx *= -1

    def draw(self, surf):
        pg.draw.rect(surf, (80, 0, 80), self.rect)


def build_level():
    # Simple static level: platforms as Rects
    platforms = []
    # ground
    platforms.append(pg.Rect(0, HEIGHT - 40, WIDTH, 40))
    # some ledges
    platforms.append(pg.Rect(100, 460, 200, 20))
    platforms.append(pg.Rect(380, 360, 180, 20))
    platforms.append(pg.Rect(600, 280, 220, 20))
    platforms.append(pg.Rect(250, 520, 120, 20))
    platforms.append(pg.Rect(480, 520, 80, 20))
    return platforms


def main():
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption("Hatena")
    clock = pg.time.Clock()

    player = Player(50, HEIGHT - 90)
    platforms = build_level()
    enemies = [Enemy(420, HEIGHT - 80, left_bound=400, right_bound=760)]
    blocks = [hatena(350, 400), hatena(500, 240)]
    items = []
    goal_rect = pg.Rect(WIDTH - 50, HEIGHT - 180, 10, 140)

    running = True
    while running:
        clock.tick(FPS)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

        keys = pg.key.get_pressed()
        player.handle_input(keys)
        player.update(platforms, blocks, items)

        for e in enemies:
            e.update()
        for i in items:
            i.update()

        # ゴール判定
        if player.rect.colliderect(goal_rect):
            print("🎉 ゴール！")
            running = False

        # 描画
        screen.fill(BG)
        for p in platforms:
            pg.draw.rect(screen, BROWN, p)
        for e in enemies:
            e.draw(screen)
        for b in blocks:
            b.draw(screen)
        for i in items:
            i.draw(screen)
        pg.draw.rect(screen, FLAG_COLOR, goal_rect)
        player.draw(screen)
        pg.display.flip()

    pg.quit()

if __name__ == '__main__':
    main()
