import pygame
import random
import sys
import time

# Initialize pygame
pygame.init()

# Screen dimensions and constants
WIDTH, HEIGHT = 800, 600
BALL_SPEED = 5
PADDLE_SPEED = 6
FPS = 60
WINNING_SCORE = 5  # Winning score to end the game

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Fonts
FONT = pygame.font.Font(None, 36)
TITLE_FONT = pygame.font.Font(None, 72)

DIFFICULTY_SPEEDS = {
    "easy": 3,
    "medium": 5,
    "hard": 7
}

# ball class handles the position, and movements
class Ball:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH // 2 - 15, HEIGHT // 2 - 15, 30, 30)
        self.speed_x = BALL_SPEED * random.choice((1, -1))
        self.speed_y = BALL_SPEED * random.choice((1, -1))

    def move(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

    def reset(self):
        """Reset the ball to the center and randomize its direction."""
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        self.speed_x = BALL_SPEED * random.choice((1, -1))
        self.speed_y = BALL_SPEED * random.choice((1, -1))

    def wall_collision(self):
        """Bounce the ball off the top and bottom walls."""
        if self.rect.top <= 0 or self.rect.bottom >= HEIGHT:
            self.speed_y *= -1

    def paddle_collision(self, paddle):
        """Bounce the ball off the paddle."""
        if self.rect.colliderect(paddle.rect):
            self.speed_x *= -1

# This calss will handle paddle movement and CPU movement
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
        if self.rect.centery < ball.rect.centery and self.rect.bottom < HEIGHT:
            self.rect.y += cpu_speed
        elif self.rect.centery > ball.rect.centery and self.rect.top > 0:
            self.rect.y -= cpu_speed

# gimmicks that will add "chaos" to the game 
class ChaosObject:
    def __init__(self):
        self.rect = pygame.Rect(random.randint(100, WIDTH - 140), random.randint(50, HEIGHT - 90), 40, 40)

    def draw(self, screen):
        pygame.draw.rect(screen, BLUE, self.rect)

# This will handles the main game logic
class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Pong with Chaos!")
        self.clock = pygame.time.Clock()
        self.ball = Ball()
        self.player_paddle = Paddle(WIDTH - 20, HEIGHT // 2 - 70)
        self.cpu_paddle = Paddle(10, HEIGHT // 2 - 70)
        self.player_score = 0
        self.cpu_score = 0
        self.running = True
        self.cpu_speed = DIFFICULTY_SPEEDS["medium"]
        self.gimmick_active = None
        self.chaos_object = None

    def reset_ball(self):
        """Reset the ball with a delay."""
        time.sleep(0.5)
        self.ball.reset()
        self.gimmick_active = None

    def display_score(self):
        player_text = FONT.render(f"{self.player_score}", True, WHITE)
        cpu_text = FONT.render(f"{self.cpu_score}", True, WHITE)
        self.screen.blit(player_text, (WIDTH - 50, 10))
        self.screen.blit(cpu_text, (30, 10))

    def spawn_chaos_object(self):
        """Spawn the chaos object randomly."""
        if not self.chaos_object and random.random() < 0.01:
            self.chaos_object = ChaosObject()

    def handle_chaos_collision(self):
        """Check if the ball collides with the chaos object."""
        if self.chaos_object and self.ball.rect.colliderect(self.chaos_object.rect):
            self.activate_hot_potato()
            self.chaos_object = None

    def activate_hot_potato(self):
        """Activate the 'hot potato' gimmick."""
        self.gimmick_active = "hot_potato"
        self.ball.speed_x *= 1.3
        self.ball.speed_y *= 1.3

    def update_hot_potato(self):
        """Handle 'hot potato' logic."""
        if self.ball.rect.left <= 0:  # CPU scores
            self.cpu_score += 1
            self.reset_ball()
        elif self.ball.rect.right >= WIDTH:  # Player scores
            self.player_score += 1
            self.reset_ball()

    def draw(self):
        self.screen.fill(BLACK)
        pygame.draw.rect(self.screen, WHITE, self.player_paddle.rect)
        pygame.draw.rect(self.screen, WHITE, self.cpu_paddle.rect)
        pygame.draw.ellipse(self.screen, RED if self.gimmick_active == "hot_potato" else WHITE, self.ball.rect)
        pygame.draw.aaline(self.screen, WHITE, (WIDTH // 2, 0), (WIDTH // 2, HEIGHT))
        self.display_score()

        # Draw chaos object
        if self.chaos_object:
            self.chaos_object.draw(self.screen)

    def title_screen(self):
        """Display the title screen."""
        while True:
            self.screen.fill(BLACK)
            title_text = TITLE_FONT.render("Pong with Chaos!", True, WHITE)
            subtitle_text = FONT.render("Press any key to start", True, WHITE)
            self.screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 2 - 100))
            self.screen.blit(subtitle_text, (WIDTH // 2 - subtitle_text.get_width() // 2, HEIGHT // 2 + 50))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    return

    def choose_difficulty(self):
        """Display the difficulty selection screen."""
        while True:
            self.screen.fill(BLACK)
            title_text = TITLE_FONT.render("Select Difficulty", True, WHITE)
            easy_text = FONT.render("1. Easy", True, WHITE)
            medium_text = FONT.render("2. Medium", True, WHITE)
            hard_text = FONT.render("3. Hard", True, WHITE)

            self.screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 2 - 100))
            self.screen.blit(easy_text, (WIDTH // 2 - easy_text.get_width() // 2, HEIGHT // 2))
            self.screen.blit(medium_text, (WIDTH // 2 - medium_text.get_width() // 2, HEIGHT // 2 + 50))
            self.screen.blit(hard_text, (WIDTH // 2 - hard_text.get_width() // 2, HEIGHT // 2 + 100))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        self.cpu_speed = DIFFICULTY_SPEEDS["easy"]
                        return
                    elif event.key == pygame.K_2:
                        self.cpu_speed = DIFFICULTY_SPEEDS["medium"]
                        return
                    elif event.key == pygame.K_3:
                        self.cpu_speed = DIFFICULTY_SPEEDS["hard"]
                        return

    def game_over_screen(self, winner):
        """Display the game over screen."""
        while True:
            self.screen.fill(BLACK)
            game_over_text = TITLE_FONT.render("Game Over!", True, WHITE)
            winner_text = FONT.render(f"{winner} Wins!", True, WHITE)
            restart_text = FONT.render("Press R to Restart or Q to Quit", True, WHITE)

            self.screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 100))
            self.screen.blit(winner_text, (WIDTH // 2 - winner_text.get_width() // 2, HEIGHT // 2))
            self.screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 100))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.__init__()  # Restart the game
                        self.run()
                    elif event.key == pygame.K_q:
                        pygame.quit()
                        sys.exit()

    def check_winner(self):
        """Check if either player has reached the winning score."""
        if self.player_score >= WINNING_SCORE:
            self.game_over_screen("Player")
        elif self.cpu_score >= WINNING_SCORE:
            self.game_over_screen("CPU")

    def run(self):
        """Main game loop."""
        self.title_screen()
        self.choose_difficulty()

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.player_paddle.move(pygame.K_UP, pygame.K_DOWN)
            self.cpu_paddle.auto_move(self.ball, self.cpu_speed)
            self.ball.move()

            # Handle collisions
            self.ball.wall_collision()
            self.ball.paddle_collision(self.player_paddle)
            self.ball.paddle_collision(self.cpu_paddle)

            # Spawn and handle chaos object
            self.spawn_chaos_object()
            self.handle_chaos_collision()

            # Update hot potato gimmick if active
            if self.gimmick_active == "hot_potato":
                self.update_hot_potato()

            self.draw()
            self.check_winner()
            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()


if __name__ == "__main__":
    Game().run()

#Update Notes:
#Chaos Object is implemented 
#Mini Hot Potato is the first of the gimmicks to be implemented


#TODOS:
#Bugs present in the code:
#Softlock glitch present when the ball is in the player's side, CPU not getting a point sometimes if it goes on the player's side from what I gathered.
#Mini Hot Potato needs to be more refined so it will stand out from other gimmicks

#Gimmicks to implement:
#1. Reverse Controls
#2. Change Ball Speeds for a short amount of time
#3. Dodgeball
#4. Invisible Ball for a set amount of time or if it hits the goal
#5. Lucky Score goes to the last paddle the ball makes contact with
#6. Penalty Score to the last paddle the ball makes contact with
#Game Modes to be Implemented:
#Single Play, BO3, BO5
#Classic Mode
