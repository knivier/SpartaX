import pygame
import yaml
import game
import sys
import time

# Load game options from YAML file
def load_options():
    try:
        with open('../properties.yaml', 'r') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        # Default options if file doesn't exist
        return {
            "game_options": {
                "mode": "two_player",
                "debug_mode": False,
                "splitscreen": False,
                "skeleton": False
            }
        }

# Save game options to YAML file
def save_options(options):
    with open('../properties.yaml', 'w') as file:
        yaml.dump(options, file)

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BLUE = (0, 0, 255)
LIGHT_BLUE = (173, 216, 230)
DARK_GRAY = (50, 50, 50)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Fonts
FONT = pygame.font.Font(None, 36)
TITLE_FONT = pygame.font.Font(None, 72)
TOOLTIP_FONT = pygame.font.Font(None, 24)

# Create screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('SpartaX Load Screen')

# Load options
options = load_options()

# Button class for better UI
class Button:
    def __init__(self, text, x, y, width, height, color, hover_color):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.hover_color = hover_color
        self.hovered = False

    def draw(self, screen):
        if self.hovered:
            pygame.draw.rect(screen, self.hover_color, self.rect)
        else:
            pygame.draw.rect(screen, self.color, self.rect)
        text_surface = FONT.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def check_hover(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)

# Fade-in animation
def fade_in(screen, width, height):
    fade_surface = pygame.Surface((width, height))
    fade_surface.fill(BLACK)
    for alpha in range(255, 0, -5):
        fade_surface.set_alpha(alpha)
        screen.blit(fade_surface, (0, 0))
        pygame.display.flip()
        pygame.time.delay(30)

# Main menu
def main_menu():
    fade_in(screen, SCREEN_WIDTH, SCREEN_HEIGHT)
    running = True
    play_button = Button('Play', 350, 250, 100, 50, GRAY, LIGHT_BLUE)
    options_button = Button('Options', 350, 320, 100, 50, GRAY, LIGHT_BLUE)
    quit_button = Button('Quit', 350, 390, 100, 50, GRAY, LIGHT_BLUE)

    while running:
        screen.fill(WHITE)

        # Draw title
        title_text = TITLE_FONT.render('SpartaX', True, DARK_GRAY)
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 100))

        # Draw buttons
        play_button.draw(screen)
        options_button.draw(screen)
        quit_button.draw(screen)

        # Tooltip for first-time users
        tooltip_text = TOOLTIP_FONT.render("Use the mouse to navigate the menu.", True, DARK_GRAY)
        screen.blit(tooltip_text, (SCREEN_WIDTH // 2 - tooltip_text.get_width() // 2, 450))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if play_button.rect.collidepoint(event.pos):
                    start_game()
                elif options_button.rect.collidepoint(event.pos):
                    options_menu()
                elif quit_button.rect.collidepoint(event.pos):
                    running = False
                    pygame.quit()
                    sys.exit()
            elif event.type == pygame.MOUSEMOTION:
                play_button.check_hover(event.pos)
                options_button.check_hover(event.pos)
                quit_button.check_hover(event.pos)

        pygame.display.flip()

# Options menu
def options_menu():
    fade_in(screen, SCREEN_WIDTH, SCREEN_HEIGHT)
    running = True
    selected_option = 0
    option_keys = list(options["game_options"].keys())
    exit_button = Button('No Save', 300, 500, 200, 50, GRAY, LIGHT_BLUE)
    save_button = Button('Save', 500, 500, 150, 50, GRAY, LIGHT_BLUE)

    while running:
        screen.fill(WHITE)

        # Draw options
        for i, key in enumerate(option_keys):
            option_text = FONT.render(f'{key.capitalize()}: {options["game_options"][key]}', True, DARK_GRAY)
            screen.blit(option_text, (100, 100 + i * 50))
            if i == selected_option:
                pygame.draw.rect(screen, BLUE, (90, 100 + i * 50, 400, 40), 3)

        # Draw buttons
        exit_button.draw(screen)
        save_button.draw(screen)

        # Tooltip for first-time users
        tooltip_text = TOOLTIP_FONT.render("Use UP/DOWN arrows to navigate, LEFT/RIGHT to change values.", True, DARK_GRAY)
        screen.blit(tooltip_text, (SCREEN_WIDTH // 2 - tooltip_text.get_width() // 2, 450))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if exit_button.rect.collidepoint(event.pos):
                    running = False
                elif save_button.rect.collidepoint(event.pos):
                    save_options(options)
                    running = False
                else:
                    for i, key in enumerate(option_keys):
                        if 100 <= event.pos[1] <= 140 + i * 50:
                            selected_option = i
                            break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % len(option_keys)
                elif event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % len(option_keys)
                elif event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    current_value = options["game_options"][option_keys[selected_option]]
                    if isinstance(current_value, bool):
                        options["game_options"][option_keys[selected_option]] = not current_value
                    elif isinstance(current_value, str):
                        if option_keys[selected_option] == "mode":
                            options["game_options"][option_keys[
                                selected_option]] = "player_vs_ai" if current_value == "two_player" else "two_player"
            elif event.type == pygame.MOUSEMOTION:
                exit_button.check_hover(event.pos)
                save_button.check_hover(event.pos)

        pygame.display.flip()

# Start game
def start_game():
    # Import and start the game from game.py
    game.run()

# Run main menu
main_menu()

# Quit Pygame
pygame.quit()