import pygame 
import random 
import os 
import sys 
 
# --- Game Settings --- 
CELL_SIZE = 20                  # Size of each grid cell
GRID_WIDTH = 30                 # Number of cells horizontally
GRID_HEIGHT = 30                # Number of cells vertically
WIDTH = CELL_SIZE * GRID_WIDTH  # Screen width in pixels
HEIGHT = CELL_SIZE * GRID_HEIGHT  # Screen height in pixels
FPS_START = 10                  # Starting speed of the snake
RECORD_FILE = "record.txt"      # File to store high score
 
# --- Colors --- 
WHITE = (255, 255, 255)
RED = (220, 20, 60)
GREEN = (0, 255, 100)
BLUE = (0, 100, 255)
BG_COLOR = (25, 25, 25)         # Background color
GRID_COLOR = (45, 45, 45)       # Grid line color

# --- Initialize Pygame ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Змейка Ultra")  # Window title
clock = pygame.time.Clock()
font = pygame.font.SysFont("consolas", 24)  # Font for text
big_font = pygame.font.SysFont("consolas", 52, bold=True)  # Font for title

# --- Load Sounds and Music ---
ASSETS = os.path.join(os.path.dirname(__file__), "assets")
EAT_SOUND_PATH = os.path.join(ASSETS, "eat.wav")
MUSIC_PATH = os.path.join(ASSETS, "bg_music.mp3")

# Load sound effect
try:
    eat_sound = pygame.mixer.Sound(EAT_SOUND_PATH)
except:
    eat_sound = None  # Ignore if not available

# Load and play background music
if os.path.exists(MUSIC_PATH):
    pygame.mixer.music.load(MUSIC_PATH)
    pygame.mixer.music.set_volume(0.3)

# --- High Score Management ---
def load_record():
    if os.path.exists(RECORD_FILE):
        try:
            with open(RECORD_FILE, "r") as f:
                return int(f.read())  # Load score from file
        except:
            return 0
    return 0

def save_record(score):
    with open(RECORD_FILE, "w") as f:
        f.write(str(score))  # Save score to file

# --- Drawing Functions ---
def draw_text(text, font, color, center):
    surface = font.render(text, True, color)
    rect = surface.get_rect(center=center)
    screen.blit(surface, rect)

def draw_grid():
    # Draw vertical lines
    for x in range(0, WIDTH, CELL_SIZE):
        pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, HEIGHT))
    # Draw horizontal lines
    for y in range(0, HEIGHT, CELL_SIZE):
        pygame.draw.line(screen, GRID_COLOR, (0, y), (WIDTH, y))

# --- Snake Class ---
class Snake:
    def __init__(self):
        self.body = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]  # Start at center
        self.direction = (0, -1)  # Initially moving up
        self.grow_pending = False

    def head(self):
        return self.body[-1]

    def change_direction(self, dx, dy):
        # Prevent reversing direction
        if (dx, dy) != (-self.direction[0], -self.direction[1]):
            self.direction = (dx, dy)

    def move(self):
        head_x, head_y = self.head()
        dx, dy = self.direction
        # Move snake with screen wrapping
        new_head = ((head_x + dx) % GRID_WIDTH, (head_y + dy) % GRID_HEIGHT)

        # Check for collision with itself
        if new_head in self.body:
            return False  # Game over

        self.body.append(new_head)

        if not self.grow_pending:
            self.body.pop(0)  # Move forward
        else:
            self.grow_pending = False  # Cancel grow

        return True

    def grow(self):
        self.grow_pending = True

    def draw(self):
        # Draw body segments
        for segment in self.body[:-1]:
            x, y = segment
            pygame.draw.rect(screen, GREEN, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
        # Draw head
        hx, hy = self.head()
        pygame.draw.rect(screen, BLUE, (hx * CELL_SIZE, hy * CELL_SIZE, CELL_SIZE, CELL_SIZE))

# --- Food Class ---
class Food:
    def __init__(self, snake_body):
        self.relocate(snake_body)

    def relocate(self, snake_body):
        # Place food in a random position not occupied by the snake
        while True:
            pos = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
            if pos not in snake_body:
                self.position = pos
                break

    def draw(self):
        x, y = self.position
        pygame.draw.rect(screen, RED, (x * CELL_SIZE + 3, y * CELL_SIZE + 3, CELL_SIZE - 6, CELL_SIZE - 6))

# --- Pause Menu ---
def pause_menu():
    draw_text("Пауза", big_font, WHITE, (WIDTH // 2, HEIGHT // 2 - 20))
    draw_text("Нажмите P для продолжения", font, WHITE, (WIDTH // 2, HEIGHT // 2 + 30))
    pygame.display.flip()
    # Wait until P is pressed
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                return

# --- Game Over Screen ---
def game_over(score, record):
    pygame.mixer.music.stop()
    screen.fill(BG_COLOR)
    draw_text("Игра окончена", big_font, RED, (WIDTH // 2, HEIGHT // 2 - 50))
    draw_text(f"Счёт: {score}", font, WHITE, (WIDTH // 2, HEIGHT // 2 + 10))
    draw_text(f"Рекорд: {record}", font, WHITE, (WIDTH // 2, HEIGHT // 2 + 50))
    draw_text("Нажмите Enter", font, WHITE, (WIDTH // 2, HEIGHT // 2 + 100))
    pygame.display.flip()
    # Wait until Enter is pressed
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                return

# --- Main Menu ---
def main_menu():
    screen.fill(BG_COLOR)
    draw_text("Змейка Ultra", big_font, GREEN, (WIDTH // 2, HEIGHT // 2 - 50))
    draw_text("Нажмите Enter для начала", font, WHITE, (WIDTH // 2, HEIGHT // 2 + 30))
    pygame.display.flip()
    # Wait until Enter is pressed
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                return

# --- Main Game Loop ---
def main():
    main_menu()
    snake = Snake()
    food = Food(snake.body)
    score = 0
    record = load_record()
    speed = FPS_START

    # Start background music
    if os.path.exists(MUSIC_PATH):
        pygame.mixer.music.play(-1)  # Loop forever

    while True:
        direction_changed = False
        clock.tick(speed)

        # Handle input
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
            elif event.type == pygame.KEYDOWN:
                if not direction_changed:
                    if event.key in [pygame.K_UP, pygame.K_w]:
                        snake.change_direction(0, -1)
                        direction_changed = True
                    elif event.key in [pygame.K_DOWN, pygame.K_s]:
                        snake.change_direction(0, 1)
                        direction_changed = True
                    elif event.key in [pygame.K_LEFT, pygame.K_a]:
                        snake.change_direction(-1, 0)
                        direction_changed = True
                    elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                        snake.change_direction(1, 0)
                        direction_changed = True
                if event.key == pygame.K_p:
                    pause_menu()

        # Move snake and check for game over
        if not snake.move():
            if score > record:
                save_record(score)
                record = score
            game_over(score, record)
            return main()  # Restart game

        # Check for eating food
        if snake.head() == food.position:
            snake.grow()
            food.relocate(snake.body)
            score += 1
            if eat_sound: eat_sound.play()
            if score % 5 == 0:
                speed += 1  # Increase speed every 5 points

        # --- Drawing Section ---
        screen.fill(BG_COLOR)
        draw_grid()
        snake.draw()
        food.draw()
        draw_text(f"Счёт: {score}", font, WHITE, (10 + 50, 15))
        draw_text(f"Рекорд: {record}", font, WHITE, (WIDTH - 120, 15))
        pygame.display.flip()

# --- Run Game ---
if __name__ == "__main__": 
    main()
