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
WINNING_SCORE = 5  # Winning score per game

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

class Ball:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH // 2 - 15, HEIGHT // 2 - 15, 30, 30)
        self.speed_x = BALL_SPEED * random.choice((1, -1))
        self.speed_y = BALL_SPEED * random.choice((1, -1))
        self.hot_potato_hits = 0
        self.last_touched_by = None

    def move(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        max_speed = 10
        self.speed_x = max(-max_speed, min(max_speed, self.speed_x))
        self.speed_y = max(-max_speed, min(max_speed, self.speed_y))

    def reset(self):
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        self.speed_x = BALL_SPEED * random.choice((1, -1))
        self.speed_y = BALL_SPEED * random.choice((1, -1))
        self.hot_potato_hits = 0
        self.last_touched_by = None
    
    def wall_collision(self):

        if self.rect.top < 0:
            print(f"Collision at TOP - Ball Position: {self.rect.topleft}, Speed: {self.speed_y}")
            self.rect.top = 0
            self.speed_y = abs(self.speed_y)
        elif self.rect.bottom > HEIGHT:
            print(f"Collision at BOTTOM - Ball Position: {self.rect.bottomright}, Speed: {self.speed_y}")
            self.rect.bottom = HEIGHT
            self.speed_y = -abs(self.speed_y)

    def paddle_collision(self, paddle, game):
        if self.rect.colliderect(paddle.rect):
            self.speed_x *= -1
            self.last_touched_by = "player" if paddle.rect.x > WIDTH // 2 else "cpu"

            # Increment hit counter only if hot potato is active
            if game.gimmick_active == "hot_potato":
                self.hot_potato_hits += 1


class Paddle:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 10, 140)
        self.active = True
    
    def reset(self):
        self.rect.y = HEIGHT // 2 - self.rect.height // 2
        self.active = True

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
    
    def draw(self, screen):
        if self.active:
            pygame.draw.rect(screen, WHITE, self.rect)


class ChaosObject:
    def __init__(self):
        self.rect = pygame.Rect(random.randint(100, WIDTH - 140), random.randint(50, HEIGHT - 90), 40, 40)

    def draw(self, screen):
        pygame.draw.rect(screen, BLUE, self.rect)

class Explosion:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 10
        self.max_radius = 80
        self.growth_rate = 8
        self.active = True
    
    def update(self):

        if self.radius < self.max_radius:
            self.radius += self.growth_rate
        else:
            self.active = False
    
    def draw(self, screen):

        if self.active:

            pygame.draw.circle(screen, RED, (self.x, self.y), self.radius, 2)

            pygame.draw.circle(screen, WHITE, (self.x, self.y), self.radius // 2)


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
        self.chaos_object = None
        self.gimmick_active = None
        self.player_games_won = 0
        self.cpu_games_won = 0
        self.classic_mode = False
        self.game_mode = "single_play"
        self.explosions = []

    def reset_ball(self):
        time.sleep(0.5)
        self.ball.reset()
        self.gimmick_active = None
        self.chaos_object = None

    def pause_game(self, duration):
        pygame.time.wait(duration)
    
    def reset_round(self):
        self.ball.reset()
        self.player_paddle.reset()
        self.cpu_paddle.reset()

    def display_score(self):
        player_text = FONT.render(f"{self.player_score}", True, WHITE)
        cpu_text = FONT.render(f"{self.cpu_score}", True, WHITE)
        self.screen.blit(player_text, (WIDTH - 50, 10))
        self.screen.blit(cpu_text, (30, 10))

    def display_game_progress(self):
        """Display the game progress for BO3 or BO5."""
        if self.game_mode in ["bo3", "bo5"]:
            progress_text = FONT.render(f"Games Won - Player: {self.player_games_won} | CPU: {self.cpu_games_won}", True, WHITE)
            self.screen.blit(progress_text, (WIDTH // 2 - progress_text.get_width() // 2, 30))

    def spawn_chaos_object(self):
        if not self.chaos_object and self.gimmick_active is None and random.random() < 0.01:
            self.chaos_object = ChaosObject()

    def handle_chaos_collision(self):
        """
        Handle collision with the chaos object.
        Only activate hot potato without triggering an explosion.
        """
        if self.chaos_object and self.ball.rect.colliderect(self.chaos_object.rect):
            self.activate_hot_potato()
            self.chaos_object = None

    def activate_hot_potato(self):
        """
        Activate the "hot potato" gimmick. Speeds up the ball.
        """
        self.gimmick_active = "hot_potato"
        self.ball.speed_x *= 1.3
        self.ball.speed_y *= 1.3

        max_speed = 10
        self.ball.speed_x = max(-max_speed, min(max_speed, self.ball.speed_x))
        self.ball.speed_y = max(-max_speed, min(max_speed, self.ball.speed_y))

    def handle_hot_potato(self):
        """
        Handle the "hot potato" gimmick behavior:
        - Reset hit counter on goal.
        - Explode the ball after too many hits.
        - Ensure opponent scores on goal.
        """
        self.ball.wall_collision()

        if self.gimmick_active == "hot_potato":
            # Check for explosion after too many hits
            if self.ball.hot_potato_hits >= 6:
                self.explosions.append(Explosion(self.ball.rect.centerx, self.ball.rect.centery))

                if self.ball.last_touched_by == "player":
                    self.player_paddle.active = False
                    self.cpu_score += 1
                elif self.ball.last_touched_by == "cpu":
                    self.cpu_paddle.active = False
                    self.player_score += 1

                self.pause_game(1000)
                self.reset_round()
                self.gimmick_active = None


    def update_normal_scoring(self):
        if self.ball.rect.left <= 0:
            self.player_score += 1
            self.reset_ball()
        
        elif self.ball.rect.right >= WIDTH:
            self.cpu_score += 1
            self.reset_ball()
    
    def update_hot_potato(self):
        if self.gimmick_active == "hot_potato":
            if self.ball.rect.right >= WIDTH:
                self.cpu_score += 1
                print("Hot Potato: Ball hit the player's goal. CPU scores!")  # Debugging statement
                self.ball.hot_potato_hits = 0  # Reset hit counter
                self.reset_ball()
        
        elif self.ball.rect.left <= 0:
            self.player_score += 1
            print("Hot Potato: Ball hit the CPU's goal. Player scores!")  # Debugging statement
            self.ball.hot_potato_hits = 0  # Reset hit counter
            self.reset_ball()


    def draw(self):
        self.screen.fill(BLACK)
        pygame.draw.rect(self.screen, WHITE, self.player_paddle.rect)
        pygame.draw.rect(self.screen, WHITE, self.cpu_paddle.rect)
        pygame.draw.ellipse(self.screen, RED if self.gimmick_active == "hot_potato" else WHITE, self.ball.rect)
        pygame.draw.aaline(self.screen, WHITE, (WIDTH // 2, 0), (WIDTH // 2, HEIGHT))
        self.display_score()
        self.display_game_progress()

        if self.chaos_object:
            self.chaos_object.draw(self.screen)
        
        for explosion in self.explosions:
            explosion.update()
            explosion.draw(self.screen)
        self.explosions = [e for e in self.explosions if e.active]

    def title_screen(self):
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
    
    def choose_classic_mode(self):

        while True:
            self.screen.fill(BLACK)
            title_text = TITLE_FONT.render("Select Mode", True, WHITE)
            classic_text = FONT.render("1. Classic Mode", True, WHITE)
            chaos_text = FONT.render("2. Chaos Mode", True, WHITE )

            self.screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 2 - 100))
            self.screen.blit(classic_text, (WIDTH // 2 - classic_text.get_width() // 2, HEIGHT // 2))
            self.screen.blit(chaos_text, (WIDTH // 2 - chaos_text.get_width() // 2, HEIGHT // 2 + 50))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        self.classic_mode = True
                        return
                    
                    elif event.key == pygame.K_2:
                        self.classic_mode = False
                        return
                    
    def choose_game_mode(self):
        while True:
            self.screen.fill(BLACK)
            title_text = TITLE_FONT.render("Choose Game Mode", True, WHITE)
            single_text = FONT.render("1. Single Play", True, WHITE)
            bo3_text = FONT.render("2. Best of 3", True, WHITE)
            bo5_text = FONT.render("3. Best of 5", True, WHITE)

            self.screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 2 - 100))
            self.screen.blit(single_text, (WIDTH // 2 - single_text.get_width() // 2, HEIGHT // 2))
            self.screen.blit(bo3_text, (WIDTH // 2 - bo3_text.get_width() // 2, HEIGHT // 2 + 50))
            self.screen.blit(bo5_text, (WIDTH // 2 - bo5_text.get_width() // 2, HEIGHT // 2 + 100))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        self.game_mode = "single_play"
                        return
                    elif event.key == pygame.K_2:
                        self.game_mode = "bo3"
                        return
                    elif event.key == pygame.K_3:
                        self.game_mode = "bo5"
                        return

    def choose_difficulty(self):
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

    def check_winning_conditions(self):
        if self.game_mode == "single_play":
            return self.player_score >= WINNING_SCORE or self.cpu_score >= WINNING_SCORE
        elif self.game_mode in ["bo3", "bo5"]:
            if self.player_score >= WINNING_SCORE:
                self.player_games_won += 1
                self.reset_scores()
            elif self.cpu_score >= WINNING_SCORE:
                self.cpu_games_won += 1
                self.reset_scores()

            required_wins = 2 if self.game_mode == "bo3" else 3
            return self.player_games_won == required_wins or self.cpu_games_won == required_wins

    def reset_scores(self):
        self.player_score = 0
        self.cpu_score = 0
        self.ball.reset()

    def game_over_screen(self):
        winner = "Player" if self.player_games_won > self.cpu_games_won else "CPU"
        while True:
            self.screen.fill(BLACK)
            title_text = TITLE_FONT.render(f"{winner} Wins!", True, WHITE)
            subtitle_text = FONT.render("Press R to Restart or Q to Quit", True, WHITE)
            self.screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 2 - 100))
            self.screen.blit(subtitle_text, (WIDTH // 2 - subtitle_text.get_width() // 2, HEIGHT // 2 + 50))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.__init__()
                        self.run()
                    elif event.key == pygame.K_q:
                        pygame.quit()
                        sys.exit()

    def run(self):
        self.title_screen()
        self.choose_classic_mode()
        self.choose_game_mode()
        self.choose_difficulty()

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.ball.move()
            self.ball.wall_collision()
            self.ball.paddle_collision(self.player_paddle, self)
            self.ball.paddle_collision(self.cpu_paddle, self)
            self.player_paddle.move(pygame.K_UP, pygame.K_DOWN)
            self.cpu_paddle.auto_move(self.ball, self.cpu_speed)
            
            if not self.classic_mode:
                self.spawn_chaos_object()
                self.handle_chaos_collision()
                self.handle_hot_potato()

            if self.gimmick_active == "hot_potato" and not self.classic_mode:
                self.update_hot_potato()
            else:
                self.update_normal_scoring()

            if self.check_winning_conditions():
                self.game_over_screen()

            self.draw()
            pygame.display.flip()
            self.clock.tick(FPS)


if __name__ == "__main__":
    Game().run()




#Update Notes:
#Fixed issue with crashing when the Hot Potato Ball gets into contact with the paddle
#Fixed Collision issues
#Hit Counter is now exclusive to hot potato and ball won't explode when in contact with the Chaos Object
#Fixed Scoring bug to where the point is awarded to the wrong player
#Added the option to choose from classic mode and chaos mode



#TODOS:
#Bugs present in the code:
#Hot Potato Explodes too early on contact with the Paddle


#Gimmicks to implement:
#1. Reverse Controls
#2. Change speed of the game for the short amount of time (Like speed of the paddle movements and the ball speed)
#3. Dodgeball
#4. Invisible Ball for a set amount of time or if it hits the goal
#5. Lucky Score goes to the last paddle the ball makes contact with (low chance)
#6. Penalty Score to the last paddle the ball makes contact with (higher chance)
