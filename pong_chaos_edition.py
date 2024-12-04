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
            if game.gimmick_active == "hot_potato" and not game.dodgeball_mode:
                self.hot_potato_hits += 1



class Paddle:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 10, 140)
        self.active = True
    
    def reset(self):
        self.rect.y = HEIGHT // 2 - self.rect.height // 2
        self.active = True

    def move(self, up_key, down_key, game):
        current_speed = PADDLE_SPEED + (2 if game.dodgeball_mode else 0)
        keys = pygame.key.get_pressed()
        if keys[up_key] and self.rect.top > 0:
            self.rect.y -= current_speed
        if keys[down_key] and self.rect.bottom < HEIGHT:
            self.rect.y += current_speed

    def auto_move(self, ball, game):
        current_speed = game.cpu_speed + (2 if game.dodgeball_mode else 0)
        if self.rect.centery < ball.rect.centery and self.rect.bottom < HEIGHT:
            self.rect.y += current_speed
        elif self.rect.centery > ball.rect.centery and self.rect.top > 0:
            self.rect.y -= current_speed
    
    def draw(self, screen):
        if self.active:
            pygame.draw.rect(screen, WHITE, self.rect)


class ChaosObject:
    def __init__(self):
        self.rect = pygame.Rect(random.randint(100, WIDTH - 140), random.randint(50, HEIGHT - 90), 40, 40)
        self.gimmick = ChaosObject.randomize_gimmick() # Call as an instance method

    def randomize_gimmick():
        return random.choice(["hot_potato", "dodgeball", "speed_change_increase", "speed_change_decrease"])

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

class Dodgeball:
    def __init__(self, x, y, speed_x, speed_y):
        self.rect = pygame.Rect(x, y, 15, 15)
        self.speed_x = speed_x
        self.speed_y = speed_y
    
    def move(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
    
    def wall_collision(self):
        if self.rect.top <= 0 or self.rect.bottom >= HEIGHT:
            self.speed_y *= -1
        if self.rect.left <= 0 or self.rect.right >= WIDTH:
            self.speed_x *= -1
    
    def draw(self, screen):
        pygame.draw.ellipse(screen, RED, self.rect)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Pong: Chaos Edition")
        self.clock = pygame.time.Clock()
        self.ball = Ball()
        self.player_paddle = Paddle(WIDTH - 20, HEIGHT // 2 - 70)
        self.cpu_paddle = Paddle(10, HEIGHT // 2 - 70)
        self.scoring_paused = False
        self.player_score = 0
        self.cpu_score = 0
        self.running = True
        self.cpu_speed = DIFFICULTY_SPEEDS["medium"]
        self.chaos_object = None
        self.gimmick_active = None
        self.dodgeballs = []
        self.dodgeball_mode = False
        self.player_games_won = 0
        self.cpu_games_won = 0
        self.classic_mode = False
        self.game_mode = "single_play"
        self.paused = False
        self.explosions = []
        self.speed_change_timer = None
        self.original_speeds = {
            "ball": (self.ball.speed_x, self.ball.speed_y),
            "paddle": PADDLE_SPEED
        }

    def reset_ball(self):
        print("Resetting ball to center position.")
        time.sleep(0.5)
        self.ball.reset()
        print(f"Ball reset to: {self.ball.rect.center}")
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
            if self.gimmick_active in ["speed_change_increase", "speed_change_decrease"]:
                self.revert_speed_changes()

            gimmick = self.chaos_object.gimmick 
            if gimmick == "hot_potato":
                self.activate_hot_potato()
            elif gimmick == "dodgeball":
                self.activate_dodgeball()
            elif gimmick == "speed_change_increase":
                self.activate_speed_change(increase = True)
            elif gimmick == "speed_change_decrease":
                self.activate_speed_change(increase = False)
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

        if self.dodgeball_mode:
            return

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
    
    def activate_dodgeball(self):
        self.gimmick_active = "dodgeball"
        self.dodgeball_mode = True
        self.dodgeballs = []
        while len(self.dodgeballs) < 5:
            x = random.randint(50, WIDTH - 50)
            y = random.randint(50, HEIGHT - 50)
            speed_x = random.choice([-BALL_SPEED, BALL_SPEED])
            speed_y = random.choice([-BALL_SPEED, BALL_SPEED])

            new_dodgeball = Dodgeball(x, y, speed_x, speed_y)
            if not any(dodgeball.rect.colliderect(new_dodgeball.rect) for dodgeball in self.dodgeballs):
                self.dodgeballs.append(new_dodgeball)


    def handle_dodgeball_mode(self):

        for dodgeball in self.dodgeballs:
            dodgeball.move()
            dodgeball.wall_collision()
            
            if dodgeball.rect.colliderect(self.player_paddle.rect):
                self.cpu_score += 1
                self.pause_game(500)
                self.reset_to_normal_mode()
                return
            elif dodgeball.rect.colliderect(self.cpu_paddle.rect):
                self.player_score += 1
                self.pause_game(500)
                self.reset_to_normal_mode()
                return
    
    def reset_to_normal_mode(self):
        self.dodgeballs = []
        self.dodgeball_mode = False
        self.gimmick_active = None
        self.reset_ball()
    
    def activate_speed_change(self, increase = True):
        global PADDLE_SPEED
        factor = 3 if increase else 0.3
        self.gimmick_active = "speed_change_increase" if increase else "speed_change_decrease"
        
        if "ball" not in self.original_speeds or "paddle" not in self.original_speeds:
            self.original_speeds["ball"] = (self.ball.speed_x, self.ball.speed_y)
            self.original_speeds["paddle"] = PADDLE_SPEED
        
        self.ball.speed_x *= factor
        self.ball.speed_y *= factor
        self.cpu_speed *= factor
        PADDLE_SPEED *= factor
        self.speed_change_timer = pygame.time.get_ticks()

    def handle_speed_change_timer(self):

        if self.speed_change_timer and pygame.time.get_ticks() - self.speed_change_timer > 5000:
            self.revert_speed_changes()
            self.speed_change_timer = None

    def revert_speed_changes(self):
        global PADDLE_SPEED

        if "ball" in self.original_speeds:
            self.ball.speed_x, self.ball.speed_y = self.original_speeds["ball"]

        if "paddle" in self.original_speeds:
            PADDLE_SPEED = self.original_speeds["paddle"]
            self.cpu_speed = DIFFICULTY_SPEEDS["medium"]

        self.original_speeds.clear()       


    def update_normal_scoring(self):

        if self.scoring_paused:
            return
        
        if self.ball.rect.right >= WIDTH:
            self.cpu_score += 1
            self.handle_scoring_event()
        elif self.ball.rect.left <= 0:
            self.player_score += 1
            self.handle_scoring_event()
    
    def handle_scoring_event(self):

        self.scoring_paused = True
        self.revert_speed_changes()
        self.reset_ball()
        
        pygame.time.set_timer(pygame.USEREVENT, 1000)
    
    def update_hot_potato(self):
        if self.gimmick_active == "hot_potato":
            if self.ball.rect.right >= WIDTH:
                self.cpu_score += 1
                print("Hot Potato: Ball hit the player's goal. CPU scores!")  # Debugging statement
                pygame.time.wait(1000)
                self.cleanup_hot_potato()
        
            elif self.ball.rect.left <= 0:
                self.player_score += 1
                print("Hot Potato: Ball hit the CPU's goal. Player scores!")  # Debugging statement
                pygame.time.wait(1000)
                self.cleanup_hot_potato()
    
    def cleanup_hot_potato(self):
        self.ball.hot_potato_hits = 0
        self.gimmick_active = None
        self.reset_round()


    def draw(self):
        self.screen.fill(BLACK)
        pygame.draw.rect(self.screen, WHITE, self.player_paddle.rect)
        pygame.draw.rect(self.screen, WHITE, self.cpu_paddle.rect)
        if not self.dodgeball_mode:
            pygame.draw.ellipse(
                self.screen,
                RED if self.gimmick_active == "hot_potato" else WHITE,
                self.ball.rect
            )
        pygame.draw.aaline(self.screen, WHITE, (WIDTH // 2, 0), (WIDTH // 2, HEIGHT))
        self.display_score()
        self.display_game_progress()

        

        

        if self.dodgeball_mode:
            for dodgeball in self.dodgeballs:
                dodgeball.draw(self.screen)

        if self.chaos_object:
            self.chaos_object.draw(self.screen)
        
        for explosion in self.explosions:
            explosion.update()
            explosion.draw(self.screen)
        self.explosions = [e for e in self.explosions if e.active]

    def title_screen(self):
        while True:
            self.screen.fill(BLACK)
            title_text = TITLE_FONT.render("Pong: Chaos Edition", True, WHITE)
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
    def pause_menu(self):
        while True:
            self.screen.fill(BLACK)
            title_text = TITLE_FONT.render("Game Paused", True, WHITE)
            continue_text = FONT.render("1. Continue", True, WHITE)
            restart_text = FONT.render("2. Restart", True, WHITE)
            menu_text = FONT.render("3. Return to the Main Menu", True, WHITE)
            quit_text = FONT.render("4. Quit the Game", True, WHITE)

            self.screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 2 - 150))
            self.screen.blit(continue_text, (WIDTH // 2 - continue_text.get_width() // 2, HEIGHT // 2 - 50))
            self.screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2))
            self.screen.blit(menu_text, (WIDTH // 2 - menu_text.get_width() // 2, HEIGHT // 2 + 50))
            self.screen.blit(quit_text, (WIDTH // 2 - quit_text.get_width() // 2, HEIGHT // 2 + 100))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        return
                    elif event.key == pygame.K_2:
                        if self.confirm_action("Restart"):
                            self.reset_game_state()
                            return
                    elif event.key == pygame.K_3:
                        if self.confirm_action("Return to the Main Menu"):
                            self.__init__()
                            self.run()
                    elif event.key == pygame.K_4:
                        if self.confirm_action("Quit the Game"):
                            pygame.quit()
                            sys.exit()
    
    def confirm_action(self, action_text):

        while True:
            self.screen.fill(BLACK)
            title_text = FONT.render(f"Are you sure you want to {action_text}?", True, WHITE)
            yes_text = FONT.render("1. Yes", True, WHITE)
            no_text = FONT.render("2. No", True, WHITE)

            self.screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 2 - 50))
            self.screen.blit(yes_text, (WIDTH // 2 - yes_text.get_width() // 2, HEIGHT // 2))
            self.screen.blit(no_text, (WIDTH // 2 - no_text.get_width() // 2, HEIGHT // 2 + 50))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        return True
                    
                    elif event.key == pygame.K_2:
                        return False
    
    def reset_game_state(self):
        self.player_score = 0
        self.cpu_score = 0
        self.player_games_won = 0
        self.cpu_games_won = 0
        self.ball.reset()
        self.player_paddle.reset()
        self.gimmick_active = None
        self.chaos_object = None
        self.explosions = []
        self.speed_change_timer = None

        self.revert_speed_changes()

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
                elif event.type == pygame.USEREVENT:
                    self.scoring_paused = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:  # Pause the game
                        self.pause_menu()

            self.ball.move()
            self.ball.wall_collision()
            self.ball.paddle_collision(self.player_paddle, self)
            self.ball.paddle_collision(self.cpu_paddle, self)
            self.player_paddle.move(pygame.K_UP, pygame.K_DOWN, self)
            self.cpu_paddle.auto_move(self.ball, self)
            
            if not self.classic_mode:
                self.spawn_chaos_object()
                self.handle_chaos_collision()
                self.handle_hot_potato()
            
            if self.gimmick_active == "hot_potato":
                self.update_hot_potato()
            elif self.gimmick_active == "dodgeball":
                self.handle_dodgeball_mode()
            else:
                self.update_normal_scoring()
            
            self.handle_speed_change_timer()


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
#Added the Pause Menu function
#Dodgeball mechanic implemented
#Speed Increase and Speed Decrese Gimmicks implemented affecting both paddles and the balls
#Minor bug fixes with hot potato causing a softlock
#Added a brief pause when the Hot Potato hits the goal



#TODOS:

#Bugs present in the code:
#Hot Potato Explodes too early on contact with the Paddle
#Ball sticking on the paddle on occasion


#Gimmicks to implement:
#1. Reverse Controls
#2. Invisible Ball for a set amount of time or if it hits the goal
#3. Lucky Score goes to the last paddle the ball makes contact with (low chance)
#4. Penalty Score to the last paddle the ball makes contact with (higher chance)

#Tips for implementing the gimmicks:
#Make sure the gimmicks are connected to the Chaos Object, there will be a logic error if they aren't connected to the Chaos Object.
#If running into issues, use AI to diagnose the problem and troubleshoot. Also analyze the code to ensure nothing is out of the oridinary
#If running into further trouble, reach out on Discord so we can troubleshoot the problem together.


#Misc:
#Add a text that tells the player which gimmick is activiated for a couple of seconds
#Add more notes for clarity
#Review the code to make sure everything looks nice and presentable once all of the gimmicks are implemented
#Tweak the Game Over Menu to ask the player "Are You Sure" much like the Pause Menu
#Once the code is complete, remove any debugging code to make the project ready to be submitted
