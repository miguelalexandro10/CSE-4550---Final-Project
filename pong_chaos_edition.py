import pygame
import random

# Initialize pygame
pygame.init()

# Screen dimensions and constants
WIDTH, HEIGHT = 800, 600
BALL_SPEED = 5
PADDLE_SPEED = 6
FPS = 60
WINNING_SCORE = 10

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Fonts
FONT = pygame.font.Font(None, 36)
LARGE_FONT = pygame.font.Font(None, 72)

# Classes
class Ball:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH // 2 - 15, HEIGHT // 2 - 15, 30, 30)
        self.speed_x = BALL_SPEED * random.choice((1, -1))
        self.speed_y = BALL_SPEED * random.choice((1, -1))

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

class Paddle:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 10, 140)

    def move(self, up_key, down_key):
        keys = pygame.key.get_pressed()
        if keys[up_key] and self.rect.top > 0:
            self.rect.y -= PADDLE_SPEED
        if keys[down_key] and self.rect.bottom < HEIGHT:
            self.rect.y += PADDLE_SPEED

    def auto_move(self, ball):
        if self.rect.centery < ball.rect.centery:
            self.rect.y += PADDLE_SPEED - 3
        elif self.rect.centery > ball.rect.centery:
            self.rect.y -= PADDLE_SPEED - 3

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

    def reset_ball(self):
        self.ball.reset()

    def display_score(self):
        player_text = FONT.render(f"{self.player_score}", True, WHITE)
        cpu_text = FONT.render(f"{self.cpu_score}", True, WHITE)
        self.screen.blit(player_text, (WIDTH // 2 + 20, 20))
        self.screen.blit(cpu_text, (WIDTH // 2 - 40, 20))

    def check_score(self):
        if self.ball.rect.left <= 0:
            self.player_score += 1
            self.reset_ball()
        elif self.ball.rect.right >= WIDTH:
            self.cpu_score += 1
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
        pygame.draw.rect(self.screen, WHITE, self.player_paddle.rect)
        pygame.draw.rect(self.screen, WHITE, self.cpu_paddle.rect)
        pygame.draw.ellipse(self.screen, WHITE, self.ball.rect)
        pygame.draw.aaline(self.screen, WHITE, (WIDTH // 2, 0), (WIDTH // 2, HEIGHT))
        self.display_score()

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            # Paddle and Ball Movement
            self.player_paddle.move(pygame.K_UP, pygame.K_DOWN)
            self.cpu_paddle.auto_move(self.ball)
            self.ball.move()

            # Collision Detection
            self.ball.wall_collision()
            self.ball.paddle_collision(self.player_paddle)
            self.ball.paddle_collision(self.cpu_paddle)

            # Scoring and Winning Conditions
            self.check_score()
            self.check_winner()

            # Drawing and Updating Display
            self.draw()
            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()

# Run the game
if __name__ == "__main__":
    Game().run()

#TODOS
#Disclaimer: I am aware that we are short on time this semester.
#But if you feel like adding a bunch of stuff is too much to handle and in such short time, 
#then we can cut down certain objectives to make this project manageable. 

#CPU Difficulty Adjustment
#Classic Gameplay, or Chaos Edition
#Game Mode Selection: Single Play, Best of 3, Best of 5
#Add a class dedicated to a "Chaos Object" that if a ball collides with it, random gimmicks will occur
#Gimmicks to implement to the Chaos Object if possible:
#1. Reverse Controls
#2. Change Ball Speed
#3. Mini Hot Potato
#4. Invisible Ball
#5. Lucky Score (+1 point) (Low Chance)
#6. Punishment (-1 point) (Higher Chance of it happening. But it is still on the low side)
#7. Turning court vertical for a short amount of time, changing the controls to left and right, instead of up and down
#8. Dodge Ball Mode
#9. Paddle size changes 
#2 Player Mode if Possible (if we are running out of time to implement this feature, then we can always cut this out)

# Make sure if possible that one of the gimmicks is tested to work properly before we add in more gimmicks.