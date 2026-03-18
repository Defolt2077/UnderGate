import arcade
import random
import math
import os

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "UnderGate"

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 50, 50)
YELLOW = (255, 255, 100)
CREAM = (255, 255, 200)
SOUL_COLOR = (255, 100, 100)
SOUL_HURT_COLOR = (255, 255, 255)
ENEMY_COLOR = (255, 100, 100)
BLUE = (100, 100, 255)
GRAY = (128, 128, 128)


class Button:

    def __init__(self, x, y, width, height, text, color, hover_color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False

    def draw(self):
        color = self.hover_color if self.is_hovered else self.color
        arcade.draw_lbwh_rectangle_filled(self.x - self.width // 2, self.y - self.height // 2,
                                          self.width, self.height, color)
        arcade.draw_lbwh_rectangle_outline(self.x - self.width // 2, self.y - self.height // 2,
                                           self.width, self.height, WHITE, 2)

        arcade.draw_text(self.text, self.x, self.y - 10, WHITE, 20, anchor_x="center")

    def check_hover(self, mouse_x, mouse_y):
        self.is_hovered = (self.x - self.width // 2 <= mouse_x <= self.x + self.width // 2 and
                           self.y - self.height // 2 <= mouse_y <= self.y + self.height // 2)
        return self.is_hovered

    def check_click(self, mouse_x, mouse_y):
        return (self.x - self.width // 2 <= mouse_x <= self.x + self.width // 2 and
                self.y - self.height // 2 <= mouse_y <= self.y + self.height // 2)


class Soul:

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 10
        self.change_x = 0
        self.change_y = 0
        self.speed = 5
        self.health = 5
        self.max_health = 5
        self.invulnerable = False
        self.invulnerable_timer = 0
        self.invulnerable_duration = 1.5
        self.blink_timer = 0
        self.hurt_effect_timer = 0

    def update(self):
        self.x += self.change_x
        self.y += self.change_y

        if self.x < 300:
            self.x = 300
        if self.x > 500:
            self.x = 500
        if self.y < 200:
            self.y = 200
        if self.y > 400:
            self.y = 400

        if self.invulnerable:
            self.invulnerable_timer -= 1 / 60
            self.blink_timer += 1

            if self.invulnerable_timer <= 0:
                self.invulnerable = False
                self.invulnerable_timer = 0
                self.blink_timer = 0

        if self.hurt_effect_timer > 0:
            self.hurt_effect_timer -= 1

    def hit(self):
        if not self.invulnerable and self.health > 0:
            self.health -= 1
            self.invulnerable = True
            self.invulnerable_timer = self.invulnerable_duration
            self.hurt_effect_timer = 10
            return True
        return False

    def draw(self):
        if self.hurt_effect_timer > 0:
            color = SOUL_HURT_COLOR
        elif self.invulnerable and (int(self.blink_timer * 10) % 2 == 0):
            color = SOUL_HURT_COLOR
        else:
            color = SOUL_COLOR

        self.draw_heart(self.x, self.y, self.radius * 1.5, color)

    def draw_heart(self, x, y, size, color):
        arcade.draw_circle_filled(x - size / 2, y + size / 3, size / 2, color)
        arcade.draw_circle_filled(x + size / 2, y + size / 3, size / 2, color)

        points = [
            (x - size, y + size / 3),
            (x + size, y + size / 3),
            (x, y - size)
        ]
        arcade.draw_polygon_filled(points, color)

        arcade.draw_circle_outline(x - size / 2, y + size / 3, size / 2, WHITE, 1)
        arcade.draw_circle_outline(x + size / 2, y + size / 3, size / 2, WHITE, 1)
        arcade.draw_line(x - size, y + size / 3, x, y - size, WHITE, 1)
        arcade.draw_line(x + size, y + size / 3, x, y - size, WHITE, 1)
        arcade.draw_line(x - size, y + size / 3, x + size, y + size / 3, WHITE, 1)


class AttackBullet:

    def __init__(self, x, y, target_x, target_y):
        self.x = x
        self.y = y
        self.radius = 8
        self.speed = 15
        self.color = YELLOW
        self.active = True

        dx = target_x - x
        dy = target_y - y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        if distance > 0:
            self.speed_x = (dx / distance) * self.speed
            self.speed_y = (dy / distance) * self.speed
        else:
            self.speed_x = 0
            self.speed_y = self.speed

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y

    def draw(self):
        arcade.draw_circle_filled(self.x, self.y, self.radius, self.color)
        arcade.draw_circle_outline(self.x, self.y, self.radius, WHITE, 2)

    def is_out_of_bounds(self):
        return (self.x < 0 or self.x > SCREEN_WIDTH or
                self.y < 0 or self.y > SCREEN_HEIGHT)


class EnemyBullet:

    def __init__(self, x, y, target_x, target_y, speed=2):
        self.x = x
        self.y = y
        self.radius = 6
        self.speed = speed
        self.color = WHITE
        self.active = True

        dx = target_x - x
        dy = target_y - y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        if distance > 0:
            self.speed_x = (dx / distance) * speed
            self.speed_y = (dy / distance) * speed
        else:
            self.speed_x = 0
            self.speed_y = speed

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y

    def draw(self):
        arcade.draw_circle_filled(self.x, self.y, self.radius, self.color)
        arcade.draw_circle_outline(self.x, self.y, self.radius, WHITE, 1)

    def is_out_of_bounds(self):
        return (self.x < 200 or self.x > 600 or
                self.y < 100 or self.y > 500)


class Enemy:

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 40
        self.pulse = 0
        self.pulse_dir = 1
        self.attack_pattern = 0
        self.pattern_timer = 0
        self.max_health = 20
        self.health = self.max_health
        self.sprite = None

        try:
            if os.path.exists("images/enemy.png"):
                self.sprite = arcade.load_texture("images/enemy.png")
        except:
            print("Не удалось загрузить спрайт врага, использую рисованного")
            self.sprite = None

    def update(self):
        self.pulse += 0.1 * self.pulse_dir
        if self.pulse > 1 or self.pulse < 0:
            self.pulse_dir *= -1

        self.pattern_timer += 0.016
        if self.pattern_timer > 8:
            self.pattern_timer = 0
            self.attack_pattern = (self.attack_pattern + 1) % 3

    def take_damage(self, damage=1):
        self.health -= damage
        return self.health <= 0

    def draw(self):
        if self.sprite:
            scale = 0.3 + self.pulse * 0.05
            sprite_rect = arcade.XYWH(
                self.x, self.y,
                self.sprite.width * scale,
                self.sprite.height * scale
            )

            arcade.draw_texture_rect(
                texture=self.sprite,
                rect=sprite_rect,
                color=arcade.color.WHITE,
                angle=0,
                alpha=255
            )
        else:
            current_radius = self.radius + self.pulse * 5
            health_percent = self.health / self.max_health

            enemy_color = (
                int(ENEMY_COLOR[0]),
                int(ENEMY_COLOR[1] * health_percent),
                int(ENEMY_COLOR[2] * health_percent)
            )

            arcade.draw_circle_filled(self.x, self.y, current_radius, enemy_color)

            arcade.draw_circle_filled(self.x - 20, self.y + 15, 8, BLACK)
            arcade.draw_circle_filled(self.x + 20, self.y + 15, 8, BLACK)
            arcade.draw_circle_filled(self.x - 23, self.y + 18, 3, WHITE)
            arcade.draw_circle_filled(self.x + 17, self.y + 18, 3, WHITE)

            if self.attack_pattern == 0:
                arcade.draw_arc_outline(self.x, self.y - 5, 30, 20, WHITE, 180, 360, 3)
            elif self.attack_pattern == 1:
                arcade.draw_arc_outline(self.x, self.y - 5, 30, 20, RED, 0, 180, 3)
            else:
                arcade.draw_arc_outline(self.x, self.y - 5, 30, 20, YELLOW, 90, 270, 3)

        bar_width = 180
        bar_height = 12
        bar_x = self.x - bar_width // 2
        bar_y = self.y + 60

        arcade.draw_lbwh_rectangle_filled(bar_x, bar_y, bar_width, bar_height, (60, 60, 60))
        arcade.draw_lbwh_rectangle_outline(bar_x, bar_y, bar_width, bar_height, WHITE, 1)

        health_width = (self.health / self.max_health) * (bar_width - 4)
        if self.health > self.max_health * 0.6:
            health_color = (0, 255, 0)
        elif self.health > self.max_health * 0.3:
            health_color = (255, 255, 0)
        else:
            health_color = (255, 0, 0)

        if health_width > 0:
            arcade.draw_lbwh_rectangle_filled(bar_x + 2, bar_y + 2, health_width, bar_height - 4, health_color)


class BattleGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(BLACK)

        self.current_state = "MENU"

        self.buttons = [
            Button(400, 350, 200, 50, "START GAME", BLUE, (100, 100, 255)),
            Button(400, 250, 200, 50, "QUIT", RED, (255, 100, 100))
        ]

        self.soul = None
        self.enemy = None
        self.enemy_bullets = []
        self.attack_bullets = []

        self.score = 0
        self.game_over = False
        self.win = False
        self.frame_count = 0
        self.bullet_timer = 0
        self.bullet_spawn_rate = 0.8
        self.hit_effects = []

        self.attack_cooldown = 0.5
        self.attack_timer = 0
        self.attack_ready = True

        self.intro_timer = 3
        self.intro_text = "FIGHT!"

        self.hurt_sound = None
        self.hit_sound = None
        self.win_sound = None
        self.lose_sound = None
        self.menu_music = None
        self.battle_music = None

        self.menu_music_player = None
        self.battle_music_player = None

        self.load_sounds()

    def load_sounds(self):
        try:
            os.makedirs("sounds", exist_ok=True)

            if os.path.exists("sounds/hurt.wav"):
                self.hurt_sound = arcade.load_sound("sounds/hurt.wav")
            if os.path.exists("sounds/hit.wav"):
                self.hit_sound = arcade.load_sound("sounds/hit.wav")
            if os.path.exists("sounds/win.wav"):
                self.win_sound = arcade.load_sound("sounds/win.wav")
            if os.path.exists("sounds/lose.wav"):
                self.lose_sound = arcade.load_sound("sounds/lose.wav")

            if os.path.exists("sounds/menu_music.mp3"):
                self.menu_music = arcade.load_sound("sounds/menu_music.mp3")
            if os.path.exists("sounds/battle_music.mp3"):
                self.battle_music = arcade.load_sound("sounds/battle_music.mp3")

        except Exception as e:
            print(f"Не удалось загрузить звуки: {e}")

    def stop_all_music(self):
        if self.menu_music_player:
            self.menu_music_player.delete()
            self.menu_music_player = None
        if self.battle_music_player:
            self.battle_music_player.delete()
            self.battle_music_player = None

    def play_menu_music(self):
        self.stop_all_music()
        if self.menu_music:
            self.menu_music_player = arcade.play_sound(self.menu_music, volume=0.3, loop=True)

    def play_battle_music(self):
        self.stop_all_music()
        if self.battle_music:
            self.battle_music_player = arcade.play_sound(self.battle_music, volume=0.3, loop=True)

    def setup_battle(self):
        self.soul = Soul(400, 300)
        self.enemy = Enemy(400, 450)
        self.enemy_bullets = []
        self.attack_bullets = []
        self.score = 0
        self.game_over = False
        self.win = False
        self.bullet_timer = 0
        self.frame_count = 0
        self.hit_effects = []
        self.attack_timer = 0
        self.attack_ready = True

    def spawn_enemy_bullets(self):
        pattern = self.enemy.attack_pattern

        if pattern == 0:
            num_bullets = random.randint(1, 2)
            speed_range = (2, 4)
        elif pattern == 1:
            num_bullets = random.randint(1, 2)
            speed_range = (3, 5)
        else:
            num_bullets = 2
            speed_range = (1, 3)

        for i in range(num_bullets):
            if pattern == 2:
                side = i % 4
            else:
                side = random.randint(0, 3)

            if side == 0:
                x = random.randint(320, 480)
                y = 420
                target_x = random.randint(320, 480)
                target_y = 180
            elif side == 1:
                x = random.randint(320, 480)
                y = 180
                target_x = random.randint(320, 480)
                target_y = 420
            elif side == 2:
                x = 280
                y = random.randint(220, 380)
                target_x = 520
                target_y = random.randint(220, 380)
            else:
                x = 520
                y = random.randint(220, 380)
                target_x = 280
                target_y = random.randint(220, 380)

            speed = random.randint(speed_range[0], speed_range[1])
            self.enemy_bullets.append(EnemyBullet(x, y, target_x, target_y, speed))

    def spawn_spiral_bullets(self):
        center_x, center_y = 400, 300
        num_bullets = 8
        self.frame_count += 1

        rotation_speed = 1

        for i in range(num_bullets):
            angle = (i * (360 / num_bullets) + self.frame_count * rotation_speed) % 360
            rad = math.radians(angle)

            radius = 100
            start_x = center_x + math.cos(rad) * radius
            start_y = center_y + math.sin(rad) * radius
            target_x = center_x - math.cos(rad) * radius
            target_y = center_y - math.sin(rad) * radius

            self.enemy_bullets.append(EnemyBullet(start_x, start_y, target_x, target_y, 5))

    def attack_enemy(self):
        if self.attack_ready and self.soul and self.enemy and not self.game_over:
            bullet = AttackBullet(self.soul.x, self.soul.y, self.enemy.x, self.enemy.y)
            self.attack_bullets.append(bullet)

            self.attack_ready = False
            self.attack_timer = self.attack_cooldown

            if self.hit_sound:
                arcade.play_sound(self.hit_sound, volume=0.2)

    def on_draw(self):
        self.clear()

        if self.current_state == "MENU":
            arcade.draw_text("UNDERGATE", 400, 500, YELLOW, 40, anchor_x="center")
            arcade.draw_text("A Python Arcade Game", 400, 450, CREAM, 20, anchor_x="center")

            for button in self.buttons:
                button.draw()

        elif self.current_state == "INTRO":
            arcade.draw_text(self.intro_text, 400, 300, YELLOW, 60, anchor_x="center")
            arcade.draw_text(f"Get Ready! {int(self.intro_timer)}", 400, 200, CREAM, 30, anchor_x="center")

        elif self.current_state == "BATTLE":
            arcade.draw_lbwh_rectangle_outline(290, 190, 220, 220, WHITE, 3)

            if self.enemy:
                self.enemy.draw()

            if self.soul:
                self.soul.draw()

            for bullet in self.enemy_bullets:
                bullet.draw()

            for bullet in self.attack_bullets:
                bullet.draw()

            if self.soul:
                for i in range(self.soul.max_health):
                    x = 50 + i * 30
                    y = 550

                    if i < self.soul.health:
                        arcade.draw_circle_filled(x, y, 8, RED)
                        arcade.draw_circle_filled(x - 3, y + 3, 3, WHITE)
                    else:
                        arcade.draw_circle_outline(x, y, 8, RED, 2)

            arcade.draw_text(f"Score: {self.score}", 50, 500, CREAM, 16)

            if self.attack_ready:
                arcade.draw_text("ATTACK READY! (Press Z)", 50, 400, YELLOW, 14)
            else:
                cooldown_text = f"Cooldown: {self.attack_timer:.1f}s"
                arcade.draw_text(cooldown_text, 50, 400, GRAY, 14)

            if self.enemy:
                patterns = ["NORMAL", "FAST", "SPIRAL"]
                arcade.draw_text(f"Pattern: {patterns[self.enemy.attack_pattern]}",
                                 50, 440, YELLOW, 14)

            if self.game_over:
                if self.win:
                    arcade.draw_text("YOU WON!", 300, 200, YELLOW, 40)
                    arcade.draw_text(f"Final Score: {self.score}", 300, 150, CREAM, 20)
                else:
                    arcade.draw_text("GAME OVER", 280, 200, RED, 40)
                arcade.draw_text("Press ESC for menu", 280, 100, CREAM, 20)

    def on_update(self, delta_time):
        if self.current_state == "INTRO":
            self.intro_timer -= delta_time
            if self.intro_timer <= 0:
                self.current_state = "BATTLE"
                self.setup_battle()
                self.play_battle_music()

        elif self.current_state == "BATTLE":
            if self.game_over:
                return

            if not self.soul or not self.enemy:
                return

            self.soul.update()
            self.enemy.update()

            if not self.attack_ready:
                self.attack_timer -= delta_time
                if self.attack_timer <= 0:
                    self.attack_ready = True
                    self.attack_timer = 0

            self.bullet_timer += delta_time

            if self.enemy.attack_pattern == 2:
                if self.bullet_timer >= 0.15:
                    self.bullet_timer = 0
                    self.spawn_spiral_bullets()
            else:
                if self.bullet_timer >= self.bullet_spawn_rate:
                    self.bullet_timer = 0
                    self.spawn_enemy_bullets()

            for bullet in self.enemy_bullets[:]:
                bullet.update()

                if bullet.active:
                    dx = bullet.x - self.soul.x
                    dy = bullet.y - self.soul.y
                    distance = (dx ** 2 + dy ** 2) ** 0.5

                    if distance < bullet.radius + self.soul.radius:
                        if self.soul.hit():
                            if self.hurt_sound:
                                arcade.play_sound(self.hurt_sound, volume=0.5)

                            self.hit_effects.append({
                                'x': self.soul.x,
                                'y': self.soul.y,
                                'timer': 10
                            })

                        bullet.active = False
                        if bullet in self.enemy_bullets:
                            self.enemy_bullets.remove(bullet)
                            self.score += 2

                if bullet.is_out_of_bounds():
                    if bullet in self.enemy_bullets:
                        self.enemy_bullets.remove(bullet)
                        self.score += 1

            for bullet in self.attack_bullets[:]:
                bullet.update()

                dx = bullet.x - self.enemy.x
                dy = bullet.y - self.enemy.y
                distance = (dx ** 2 + dy ** 2) ** 0.5

                if distance < bullet.radius + self.enemy.radius:
                    if self.hit_sound:
                        arcade.play_sound(self.hit_sound, volume=0.4)

                    if self.enemy.take_damage():
                        self.game_over = True
                        self.win = True
                        if self.win_sound:
                            arcade.play_sound(self.win_sound, volume=0.7)
                        self.stop_all_music()

                    if bullet in self.attack_bullets:
                        self.attack_bullets.remove(bullet)
                        self.score += 10
                    continue

                if bullet.is_out_of_bounds():
                    if bullet in self.attack_bullets:
                        self.attack_bullets.remove(bullet)

            for effect in self.hit_effects[:]:
                effect['timer'] -= 1
                if effect['timer'] <= 0:
                    self.hit_effects.remove(effect)

            if self.soul.health <= 0 and not self.game_over:
                self.game_over = True
                self.win = False
                if self.lose_sound:
                    arcade.play_sound(self.lose_sound, volume=0.7)
                self.stop_all_music()

    def on_key_press(self, key, modifiers):
        if self.current_state == "BATTLE" and not self.game_over:
            if key == arcade.key.LEFT or key == arcade.key.A:
                self.soul.change_x = -self.soul.speed
            elif key == arcade.key.RIGHT or key == arcade.key.D:
                self.soul.change_x = self.soul.speed
            elif key == arcade.key.UP or key == arcade.key.W:
                self.soul.change_y = self.soul.speed
            elif key == arcade.key.DOWN or key == arcade.key.S:
                self.soul.change_y = -self.soul.speed
            elif key == arcade.key.Z:
                self.attack_enemy()

        if key == arcade.key.ESCAPE:
            self.current_state = "MENU"
            self.play_menu_music()

    def on_key_release(self, key, modifiers):
        if self.current_state == "BATTLE" and not self.game_over and self.soul:
            if key == arcade.key.LEFT or key == arcade.key.A:
                self.soul.change_x = 0
            elif key == arcade.key.RIGHT or key == arcade.key.D:
                self.soul.change_x = 0
            elif key == arcade.key.UP or key == arcade.key.W:
                self.soul.change_y = 0
            elif key == arcade.key.DOWN or key == arcade.key.S:
                self.soul.change_y = 0

    def on_mouse_motion(self, x, y, dx, dy):
        if self.current_state == "MENU":
            for button in self.buttons:
                button.check_hover(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        if self.current_state == "MENU":
            for i, btn in enumerate(self.buttons):
                if btn.check_click(x, y):
                    if i == 0:
                        self.current_state = "INTRO"
                        self.intro_timer = 3
                    elif i == 1:
                        arcade.close_window()


def main():
    game = BattleGame()
    game.play_menu_music()
    arcade.run()


if __name__ == "__main__":
    main()