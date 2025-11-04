import os
import sys
import random
import pygame as pg

WIDTH, HEIGHT = 900, 600
FPS = 60
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# 色関係を宣言
GROUND = (220, 235, 237)
FLOATING_ICE = (53, 94, 144)
HATENA = (255, 255, 0)

ground_y = HEIGHT - 50
stage_index = 0
ground_platforms = []
floating_platforms = []
hatena_platforms = []


class Player:
    def __init__(self, x, y):
        self.rect = pg.Rect(x, y, 40, 50)
        self.vx = 0.0
        self.vy = 0.0
        self.speed = 5
        self.jump_power = 14
        self.on_ground = False

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

    def update(self, platforms):
        self.rect.x += int(self.vx)
        self.collide(self.vx, 0, platforms)
        self.apply_gravity()
        self.rect.y += int(self.vy)
        self.on_ground = False
        self.collide(0, self.vy, platforms)

        # 画面左に進めないようにする
        if self.rect.left < 0:
            self.rect.left = 0
            self.vx = 0

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
        pg.draw.rect(surf, (255, 0, 0), self.rect)


class Enemy:
    def __init__(self, x, y, w=40, h=40, left_bound=None, right_bound=None):
        self.rect = pg.Rect(x, y, w, h)
        self.vx = 2
        self.left_bound = left_bound
        self.right_bound = right_bound

    def update(self):
        self.rect.x += self.vx
        if self.left_bound is not None and self.rect.left < self.left_bound:
            self.rect.left = self.left_bound
            self.vx *= -1
        if self.right_bound is not None and self.rect.right > self.right_bound:
            self.rect.right = self.right_bound
            self.vx *= -1

    def draw(self, surf):
        pg.draw.rect(surf, (80, 0, 80), self.rect)


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
        pg.Rect(100, 450, 50, 50),
        pg.Rect(250, 350, WIDTH, 50)
    ]
    hatena_platforms = [pg.Rect(300, 200, 50, 50)]
    enemies = [Enemy(700, 310)]
    return ground_platforms, floating_platforms, hatena_platforms, enemies


def build_stage2():
    """
    2つ目のステージを生成する関数
    """
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
    """
    3つ目のステージを生成する関数
    """
    ground_platforms = [pg.Rect(0, ground_y, WIDTH, 40)]
    floating_platforms = [
        pg.Rect(0, 200, 250, 50),
        pg.Rect(300, 350, 200, 50),
        pg.Rect(600, 450, 250, 50)
    ]
    hatena_platforms = [
        pg.Rect(50, 100, 50, 50),
        pg.Rect(700, 300, 50, 50)
        ]
    enemies = [FoallingEnemy(300, 0), Enemy(200, 510)]
    return ground_platforms, floating_platforms, hatena_platforms, enemies


def build_stage4():
    """
    4つ目のステージを生成する関数
    """
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
    """
    5つ目のステージを生成する関数
    """
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
    hatena_platforms = [pg.Rect(750, 100, 50, 50)]
    enemies = [Enemy(350, ground_y - 40),Enemy(450, ground_y - 40),Enemy(550, ground_y - 40),Enemy(650, ground_y - 40)]
    return ground_platforms, floating_platforms, hatena_platforms, enemies


def build_stage6():
    """
    6つ目のステージを生成する関数
    """
    ground_platforms = [pg.Rect(0, ground_y, WIDTH, 40)]
    floating_platforms = [
        pg.Rect(0, 500, 50, 50),
        pg.Rect(350, 500, 200, 50),
        pg.Rect(300, 300, 250, 50),
        pg.Rect(650, 400, 50, 50),
        pg.Rect(700, 450, 200, 50)
    ]
    hatena_platforms = [pg.Rect(400, 200, 50, 50)]
    enemies = [FallingEnemy(200, 0)]
    return ground_platforms, floating_platforms, hatena_platforms, enemies


def build_stage7():
    """
    7つ目のステージを生成する関数
    """
    ground_platforms = [
        pg.Rect(0, ground_y, 250, 40),
        pg.Rect(350, ground_y, 350, 40),
        pg.Rect(800, ground_y, 100, 40)
    ]
    floating_platforms = []
    hatena_platforms = [pg.Rect(150, 450, 50, 50)]
    enemies = [FallingEnemy(500, 0)]
    return ground_platforms, floating_platforms, hatena_platforms, enemies


def build_stage8():
    """
    8つ目のステージを生成する関数
    戻り値：地面のリスト、浮島のリスト、はてなブロックのリスト
    """
    ground_platforms = [pg.Rect(0, ground_y, WIDTH, 40)]
    floating_platforms = [
        pg.Rect(150, 500, 50, 50),
        pg.Rect(200, 400, 250, 50),
        pg.Rect(750, 500, 50, 50),
        pg.Rect(500, 400, 250, 50)
    ]
    hatena_platforms = [pg.Rect(450, 250, 50, 50)]
    enemies = [Enemy(700, ground_y - 40), FallingEnemy(150, 0)]
    return ground_platforms, floating_platforms, hatena_platforms, enemies


def build_stage9():
    """
    9つ目のステージを生成する関数
    """
    ground_platforms = [pg.Rect(0, ground_y, WIDTH, 40)]
    floating_platforms = [pg.Rect(150, 450, 150, 50),pg.Rect(300, 350, 150, 50), pg.Rect(400, 250, 150, 50),pg.Rect(500, 350, 150, 50),pg.Rect(650, 450, 150, 50)]
    hatena_platforms = []
    enemies = [Enemy(300, ground_y - 40)]
    return ground_platforms, floating_platforms, hatena_platforms, enemies


def build_stage10():
    """
    10つ目のステージを生成する関数
    """
    ground_platforms = [pg.Rect(0, ground_y, 550, 40),pg.Rect(650, ground_y, 250, 40)]
    floating_platforms = [pg.Rect(150, 500, 400, 50),pg.Rect(250, 450, 300, 50),pg.Rect(350, 400, 200, 50),pg.Rect(450, 350, 100, 50),pg.Rect(650, 350, 250, 200),pg.Rect(700, 300, 200, 50)]
    hatena_platforms = []
    enemies = [FalingEnemy(750, 0)]
    return ground_platforms, floating_platforms, hatena_platforms, enemies


def build_goal():
    """
    ゴールステージ画面を生成する関数。旗に触れるとゴールする。
    戻り値：ステージ名、地面のリスト、ゴールのリスト(中身は１つだけ)
    """
    ground_platforms = [pg.Rect(0, ground_y, WIDTH, 50)]
    goal_platforms = []  # ゴール処理
    return ground_platforms, goal_platforms

#STAGE_BUILDERS = [build_stage1,build_stage2,build_stage3,build_stage4,build_stage5,build_stage6,build_stage7,build_stage8,build_stage9,build_stage10]
STAGE_BUILDERS = [build_stage10]  # デバッグ用


def main():
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    clock = pg.time.Clock()
    hatena_img = pg.image.load("hatena.png").convert_alpha()
    bg_img = pg.image.load("background.png").convert()

    player = Player(50, HEIGHT - 90)

    global stage_index
    if(stage_index == 0):  # 最初のステージ構築
        ground_platforms, floating_platforms, hatena_platforms,enemies = random.choice(STAGE_BUILDERS)()
    platforms = ground_platforms + floating_platforms + hatena_platforms + enemies
    goal_platforms = []
    font = pg.font.Font(None, 36)
    score = 0
    running = True

    while running:
        dt = clock.tick(FPS) / 1000.0
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

        keys = pg.key.get_pressed()
        player.handle_input(keys)
        player.update(platforms)

        for e in enemies:
            e.update()

        # 穴に落ちたら死亡
        if player.rect.top > HEIGHT:
            player = Player(50, HEIGHT - 90)
            break

        # ステージ切り替え
        if player.rect.right > WIDTH:
            enemies = []
            if stage_index == 5:
                # ゴール
                ground_platforms = []
                floating_platforms = []
                hatena_platforms = []
                ground_platforms, goal_platforms = build_goal()
                platforms = ground_platforms + goal_platforms
            else:
                # 次のステージ
                ground_platforms = []
                floating_platforms = []
                hatena_platforms = []
                enemies = []
                ground_platforms, floating_platforms, hatena_platforms, enemies = random.choice(STAGE_BUILDERS)()
                platforms = ground_platforms + floating_platforms + hatena_platforms + enemies
                stage_index += 1

            player.rect.left = 0
            player.update(platforms)

        # 描画
        screen.blit(bg_img, (0, 0))

        # 地面・浮島・はてなブロック・ゴール描画
        for p in ground_platforms:
            pg.draw.rect(screen, GROUND, p)
        for p in floating_platforms:
            pg.draw.rect(screen, FLOATING_ICE, p)
        for p in hatena_platforms:
            img = pg.transform.scale(hatena_img, (p.width, p.height))
            screen.blit(img, p.topleft)
        for p in enemies:
            p.draw(screen)
        if stage_index == 5:
            for g in goal_platforms:
                pg.draw.rect(screen, (255, 215, 0), g)

        player.draw(screen)
        txt = font.render(f'Score: {score}', True, (255, 255, 255))
        screen.blit(txt, (10, 10))
        sea = pg.Surface((WIDTH, HEIGHT-30), pg.SRCALPHA)
        sea.fill((0, 98, 197, 127))
        screen.blit(sea, (0, HEIGHT-30))
        pg.display.flip()

    pg.quit()


if __name__ == '__main__':
    main()
