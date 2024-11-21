import pygame
import random
import sys

# Initialize pygame
pygame.init()

# Initialize pygame mixer
pygame.mixer.init()

# Screen dimensions and constants
WIDTH, HEIGHT = 800, 600
BALL_SPEED = 5
PADDLE_SPEED = 6
FPS = 60
WINNING_SCORE = 10

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PLAYER_PADDLE_COLOR = (0, 0, 255)  # Blue for the player paddle
CPU_PADDLE_COLOR = (255, 0, 0)  # Red for the CPU paddle

# Load sound effects
paddle_hit_sound = pygame.mixer.Sound("paddle_hit.wav")
paddle_hit_sound.set_volume(0.3)  # Volume between 0.0 and 1.0
score_sound = pygame.mixer.Sound("score_point.wav")
score_sound.set_volume(0.5)
start_sound = pygame.mixer.Sound("title_screen_sound.mp3")
start_sound.set_volume(0.8)

pop_sound = pygame.mixer.Sound("pop_sound.mp3")  # Adjust path as needed
pop_sound.set_volume(0.3)  # Set volume level between 0.0 and 1.0

# Fonts
FONT = pygame.font.Font(None, 36)
LARGE_FONT = pygame.font.Font(None, 72)

# Difficulty speeds for CPU
DIFFICULTY_SPEEDS = {
    "easy": 3,
    "medium": 5,
    "hard": 7
}


# Classes for the ball, paddle, etc...
class Ball:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH // 2 - 15, HEIGHT // 2 - 15, 30, 30)
        self.speed_x = BALL_SPEED * random.choice((1, -1))
        self.speed_y = BALL_SPEED * random.choice((1, -1))
        self.color = WHITE  # Default color

    def move(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

    def reset(self):
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        self.speed_x *= random.choice((1, -1))
        self.speed_y *= random.choice((1, -1))

    def wall_collision(self):
        if self.rect.top <= 0 or self.rect.bottom >= HEIGHT:
            self.speed_y *= -1

    def paddle_collision(self, paddle):
        if self.rect.colliderect(paddle.rect):
            self.speed_x *= -1
            paddle_hit_sound.play()  # Play paddle hit sound

    def draw(self, screen):
        pygame.draw.ellipse(screen, self.color, self.rect)  # Draw the ball with the current color


class Paddle:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 10, 140)

    def move(self, up_key, down_key):
        keys = pygame.key.get_pressed()
        if keys[up_key] and self.rect.top > 0:
            self.rect.y -= PADDLE_SPEED
        if keys[down_key] and self.rect.bottom < HEIGHT:
            self.rect.y += PADDLE_SPEED

    def auto_move(self, ball, cpu_speed):
        if self.rect.centery < ball.rect.centery:
            self.rect.y += cpu_speed
        elif self.rect.centery > ball.rect.centery:
            self.rect.y -= cpu_speed


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Pong")
        self.clock = pygame.time.Clock()
        self.ball = Ball()
        self.player_paddle = Paddle(WIDTH - 20, HEIGHT // 2 - 70)
        self.cpu_paddle = Paddle(10, HEIGHT // 2 - 70)
        self.player_score = 0
        self.cpu_score = 0
        self.running = True
        self.cpu_speed = DIFFICULTY_SPEEDS["medium"]
        self.gimmick_active = False #Gimmick Timer
        self.gimmick_timer = 0 #Gimmick Timer
        self.color_gimmick_active = False  # Color-changing gimmick
        self.color_gimmick_timer = 0  # Timer for color gimmick

    def choose_difficulty(self):
        choosing = True
        while choosing:
            self.screen.fill(BLACK)
            easy_text = FONT.render("Easy: E", True, WHITE)
            medium_text = FONT.render("Medium: M", True, WHITE)
            hard_text = FONT.render("Hard: H", True, WHITE)
            self.screen.blit(easy_text, (WIDTH // 2 - easy_text.get_width() // 2, HEIGHT // 2 - 60))
            self.screen.blit(medium_text, (WIDTH // 2 - medium_text.get_width() // 2, HEIGHT // 2))
            self.screen.blit(hard_text, (WIDTH // 2 - hard_text.get_width() // 2, HEIGHT // 2 + 60))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_e:
                        self.cpu_speed = DIFFICULTY_SPEEDS["easy"]
                        choosing = False
                    elif event.key == pygame.K_m:
                        self.cpu_speed = DIFFICULTY_SPEEDS["medium"]
                        choosing = False
                    elif event.key == pygame.K_h:
                        self.cpu_speed = DIFFICULTY_SPEEDS["hard"]
                        choosing = False

    def reset_ball(self):
        self.ball.reset()

    def display_score(self):
        player_text = FONT.render(f"{self.player_score}", True, WHITE)
        cpu_text = FONT.render(f"{self.cpu_score}", True, WHITE)
        self.screen.blit(player_text, (WIDTH - 50, 10))
        self.screen.blit(cpu_text, (30, 10))

    def check_score(self):
        if self.ball.rect.left <= 0:
            self.player_score += 1
            score_sound.play()  # Play scoring sound
            self.reset_ball()
        elif self.ball.rect.right >= WIDTH:
            self.cpu_score += 1
            score_sound.play()  # Play scoring sound
            self.reset_ball()

    def display_winner(self, text):
        win_text = LARGE_FONT.render(text, True, WHITE)
        self.screen.blit(win_text, (WIDTH // 2 - win_text.get_width() // 2, HEIGHT // 2 - win_text.get_height() // 2))
        pygame.display.flip()
        pygame.time.delay(3000)
        self.running = False

    def check_winner(self):
        if self.player_score >= WINNING_SCORE:
            self.display_winner("Player Wins!")
        elif self.cpu_score >= WINNING_SCORE:
            self.display_winner("CPU Wins!")

    def draw(self):
        self.screen.fill(BLACK)
        pygame.draw.rect(self.screen, PLAYER_PADDLE_COLOR, self.player_paddle.rect)
        pygame.draw.rect(self.screen, CPU_PADDLE_COLOR, self.cpu_paddle.rect)
        self.ball.draw(self.screen)  # Call the ball's draw method with the correct color
        pygame.draw.aaline(self.screen, WHITE, (WIDTH // 2, 0), (WIDTH // 2, HEIGHT))
        self.display_score()
        if self.gimmick_active:  # Display gimmick message
            gimmick_text = FONT.render("GIMMICK: CONTROLS REVERSED!", True, (255, 0, 0))
            self.screen.blit(gimmick_text, (WIDTH // 2 - gimmick_text.get_width() // 2, 50))


    def start_screen(self):
        start_sound.play()  # Play the game start sound
        self.screen.fill(BLACK)
        start_text = LARGE_FONT.render("Press any key to begin!", True, WHITE)
        self.screen.blit(start_text,
                         (WIDTH // 2 - start_text.get_width() // 2, HEIGHT // 2 - start_text.get_height() // 2))
        pygame.display.flip()

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    waiting = False

    def run(self):
        self.start_screen()  # Display Main Menu
        self.choose_difficulty()  # Difficulty Selection

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            # Randomly activate gimmick
            if not self.gimmick_active and random.random() < 0.005:
                self.gimmick_active = True
                self.gimmick_timer = pygame.time.get_ticks()

            # Randomly activate color-changing gimmick
            if not self.color_gimmick_active and random.random() < 0.005:
                self.color_gimmick_active = True
                self.color_gimmick_timer = pygame.time.get_ticks()
                pop_sound.play()

            # Manage paddle controls
            if not self.gimmick_active:
                self.player_paddle.move(pygame.K_UP, pygame.K_DOWN)
                self.cpu_paddle.auto_move(self.ball, self.cpu_speed)
            else:
                self.player_paddle.move(pygame.K_DOWN, pygame.K_UP)
                self.cpu_paddle.auto_move(self.ball, self.cpu_speed)

                # Deactivate gimmick after 2 seconds
                if pygame.time.get_ticks() - self.gimmick_timer >= 2000:
                    self.gimmick_active = False

            # Manage color gimmick
            if self.color_gimmick_active:
                if pygame.time.get_ticks() - self.color_gimmick_timer < 500:
                    self.ball.color = (0, 0, 0)  # Change ball color to black
                else:
                    self.color_gimmick_active = False
                    self.ball.color = WHITE  # Reset ball color back to white

            self.ball.move()
            self.ball.wall_collision()
            self.ball.paddle_collision(self.player_paddle)
            self.ball.paddle_collision(self.cpu_paddle)

            self.check_score()
            self.check_winner()

            self.draw()
            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()


if __name__ == "__main__":
    Game().run()

# TODOS
# Disclaimer: I am aware that we are short on time this semester.
# But if you feel like adding a bunch of stuff is too much to handle and in such short time,
# then we can cut down certain objectives to make this project manageable.

# CPU Difficulty Adjustment
# Classic Gameplay, or Chaos Edition
# Game Mode Selection: Single Play, Best of 3, Best of 5
# Add a class dedicated to a "Chaos Object" that if a ball collides with it, random gimmicks will occur
# Gimmicks to implement to the Chaos Object if possible:
# 1. Reverse Controls
# 2. Change Ball Speed
# 3. Mini Hot Potato
# 4. Invisible Ball
# 5. Lucky Score (+1 point) (Low Chance)
# 6. Punishment (-1 point) (Higher Chance of it happening. But it is still on the low side)
# 7. Turning court vertical for a short amount of time, changing the controls to left and right, instead of up and down
# 8. Dodge Ball Mode
# 9. Paddle size changes
# 2 Player Mode if Possible (if we are running out of time to implement this feature, then we can always cut this out)

# Make sure if possible that one of the gimmicks is tested to work properly before we add in more gimmicks.

