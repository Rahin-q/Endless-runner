import random
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle, Line
from kivy.clock import Clock
from kivy.core.window import Window

# ---------------- Config ----------------
WIDTH, HEIGHT = Window.width, Window.height
GROUND_Y = 60

GRAVITY = -0.9
JUMP_VELOCITY = 16


class Player:
    def __init__(self):
        self.width = 40
        self.height = 50
        self.x = 80
        self.y = GROUND_Y
        self.vel_y = 0
        self.is_jumping = False
        self.is_ducking = False

    def jump(self):
        if not self.is_jumping:
            self.vel_y = JUMP_VELOCITY
            self.is_jumping = True

    def duck(self, state):
        if not self.is_jumping:
            self.is_ducking = state

    def current_height(self):
        return self.height // 2 if self.is_ducking else self.height

    def update(self):
        self.y += self.vel_y
        self.vel_y += GRAVITY

        if self.y <= GROUND_Y:
            self.y = GROUND_Y
            self.vel_y = 0
            self.is_jumping = False

    def get_rect(self):
        h = self.current_height()
        return (self.x, self.y, self.width, h)


class Obstacle:
    def __init__(self, x, speed):
        self.type = random.choice(["ground", "air"])
        self.width = 30
        self.speed = speed
        self.x = x

        if self.type == "ground":
            self.height = random.randint(30, 60)
            self.y = GROUND_Y
        else:
            self.height = 25
            self.y = GROUND_Y + 70

    def update(self):
        self.x -= self.speed

    def get_rect(self):
        return (self.x, self.y, self.width, self.height)

    def off_screen(self):
        return self.x + self.width < 0


def rects_collide(r1, r2):
    x1, y1, w1, h1 = r1
    x2, y2, w2, h2 = r2
    return x1 < x2 + w2 and x1 + w1 > x2 and y1 < y2 + h2 and y1 + h1 > y2


class GameWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        global WIDTH, HEIGHT
        WIDTH, HEIGHT = Window.width, Window.height

        self.score_label = Label(
            text="Score: 0",
            font_size=24,
            pos=(20, HEIGHT - 50),
            size=(200, 40),
            color=(0, 0, 0, 1),
        )
        self.add_widget(self.score_label)

        self.info_label = Label(
            text="",
            font_size=30,
            pos=(0, HEIGHT / 2 - 80),
            size=(WIDTH, 60),
            color=(0.7, 0, 0, 1),
        )
        self.add_widget(self.info_label)

        self.reset_game()
        Clock.schedule_interval(self.update, 1.0 / 60.0)
        Window.bind(size=self.on_window_resize)

    def on_window_resize(self, instance, size):
        global WIDTH, HEIGHT
        WIDTH, HEIGHT = size
        self.score_label.pos = (20, HEIGHT - 50)
        self.info_label.pos = (0, HEIGHT / 2 - 80)
        self.info_label.size = (WIDTH, 60)

    def reset_game(self):
        self.player = Player()
        self.obstacles = []
        self.score = 0
        self.speed = 6
        self.spawn_timer = 0
        self.game_over = False
        self.info_label.text = ""

    def on_touch_down(self, touch):
        if self.game_over:
            self.reset_game()
            return True

        if touch.y < HEIGHT * 0.35:
            self.player.duck(True)
        else:
            self.player.jump()
        return True

    def on_touch_up(self, touch):
        self.player.duck(False)
        return True

    def update(self, dt):
        if not self.game_over:
            self.player.update()

            self.spawn_timer += 1
            spawn_delay = max(35, 70 - self.score // 5)
            if self.spawn_timer >= spawn_delay:
                self.spawn_timer = 0
                self.obstacles.append(Obstacle(WIDTH + 20, self.speed))

            for obs in self.obstacles:
                obs.update()
            self.obstacles = [o for o in self.obstacles if not o.off_screen()]

            player_rect = self.player.get_rect()
            for obs in self.obstacles:
                if rects_collide(player_rect, obs.get_rect()):
                    self.game_over = True
                    self.info_label.text = "GAME OVER - Tap to restart"

            self.score += 1
            if self.score % 300 == 0:
                self.speed += 1

            self.score_label.text = f"Score: {self.score}"

        self.draw()

    def draw(self):
        self.canvas.clear()
        with self.canvas:
            Color(0.53, 0.81, 0.92, 1)
            Rectangle(pos=(0, 0), size=(WIDTH, HEIGHT))

            Color(0.87, 0.72, 0.53, 1)
            Rectangle(pos=(0, 0), size=(WIDTH, GROUND_Y))
            Color(0, 0, 0, 1)
            Line(points=[0, GROUND_Y, WIDTH, GROUND_Y], width=1.5)

            Color(0.78, 0.12, 0.12, 1)
            px, py, pw, ph = self.player.get_rect()
            Rectangle(pos=(px, py), size=(pw, ph))

            for obs in self.obstacles:
                if obs.type == "ground":
                    Color(0.13, 0.55, 0.13, 1)
                else:
                    Color(0.4, 0.4, 0.4, 1)
                ox, oy, ow, oh = obs.get_rect()
                Rectangle(pos=(ox, oy), size=(ow, oh))


class EndlessRunnerApp(App):
    def build(self):
        return GameWidget()


if __name__ == "__main__":
    EndlessRunnerApp().run()
